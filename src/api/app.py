"""FastAPI application for invoice processing workflow."""

import uuid
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import json
import os
import shutil
from pathlib import Path
from src.graph.builder import build_invoice_graph, create_initial_state
from src.config.workflow_loader import WorkflowConfigLoader
from src.storage.human_review_repo import HumanReviewRepository
from src.logging.logger import log_resume_event

app = FastAPI(title="Langie - Invoice Processing Agent", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global graph and dependencies (initialized on startup)
graph = None
checkpoint_store = None
human_review_repo = None
workflow_config = None


@app.on_event("startup")
async def startup():
    """Initialize graph and dependencies on startup."""
    global graph, checkpoint_store, human_review_repo, workflow_config
    
    loader = WorkflowConfigLoader()
    workflow_config = loader.get_config()
    
    graph, checkpoint_store, human_review_repo = build_invoice_graph()
    
    # Initialize human review repo
    human_review_repo._init_db()


# Pydantic models for API requests/responses

class InvoicePayload(BaseModel):
    """Invoice payload model."""
    invoice_id: str
    vendor_name: str
    vendor_tax_id: Optional[str] = None
    invoice_date: str
    due_date: str
    amount: float
    currency: str = "USD"
    line_items: list[Dict[str, Any]]
    attachments: list[str] = []


class WorkflowRunResponse(BaseModel):
    """Workflow run response."""
    thread_id: str
    status: str
    checkpoint_id: Optional[str] = None
    review_url: Optional[str] = None
    message: str


class HumanReviewItem(BaseModel):
    """Human review item."""
    checkpoint_id: str
    invoice_id: str
    vendor_name: str
    amount: float
    created_at: str
    reason_for_hold: str
    mismatch_reason: Optional[str] = None
    failed_stage: Optional[str] = None
    review_url: str


class PendingReviewsResponse(BaseModel):
    """Pending reviews response."""
    items: list[HumanReviewItem]


class HumanDecisionRequest(BaseModel):
    """Human decision request."""
    checkpoint_id: str
    decision: str  # "ACCEPT" or "REJECT"
    notes: Optional[str] = None
    reviewer_id: Optional[str] = None  # Optional - will be auto-generated if not provided


class HumanDecisionResponse(BaseModel):
    """Human decision response."""
    resume_token: str
    next_stage: str
    message: str


@app.post("/workflow/run", response_model=WorkflowRunResponse)
async def run_workflow(
    invoice: str = Form(...),  # JSON string of invoice data
    file_count: str = Form("0"),
    background_tasks: BackgroundTasks = None,
    file_0: UploadFile = File(None),
    file_1: UploadFile = File(None),
    file_2: UploadFile = File(None),
    file_3: UploadFile = File(None),
    file_4: UploadFile = File(None)
):
    """
    Start invoice processing workflow with optional file uploads.
    
    Args:
        invoice: Invoice payload as JSON string
        file_count: Number of uploaded files
        file_0 to file_4: Optional uploaded files (PDF/images for OCR)
        background_tasks: Background tasks
        
    Returns:
        Workflow run response
    """
    try:
        # Handle both form data (with file uploads) and JSON body
        if invoice:
            # Form data with file uploads
            invoice_data = json.loads(invoice)
            
            # Create attachments directory if it doesn't exist
            attachments_dir = Path("./test_data/uploaded")
            attachments_dir.mkdir(parents=True, exist_ok=True)
            
            # Save uploaded files and update attachment paths
            attachment_paths = []
            file_count_int = int(file_count or "0")
            
            # Collect all uploaded files from function parameters
            uploaded_files_list = [file_0, file_1, file_2, file_3, file_4]
            
            # Save files
            for uploaded_file in uploaded_files_list:
                if uploaded_file and uploaded_file.filename:
                    # Sanitize filename
                    safe_filename = "".join(c for c in uploaded_file.filename if c.isalnum() or c in ".-_")
                    file_path = attachments_dir / safe_filename
                    
                    # Save file
                    with open(file_path, "wb") as buffer:
                        shutil.copyfileobj(uploaded_file.file, buffer)
                    
                    attachment_paths.append(str(file_path))
                    # Log file save
                    print(f"Saved uploaded file: {file_path}")
            
            # Update invoice data with attachment paths
            invoice_data["attachments"] = attachment_paths + (invoice_data.get("attachments", []) or [])
            
            # Create InvoicePayload object for validation
            invoice_payload = InvoicePayload(**invoice_data)
        else:
            raise HTTPException(status_code=400, detail="Invoice data is required")
        
        # Create initial state
        initial_state = create_initial_state(
            invoice_payload.model_dump() if hasattr(invoice_payload, 'model_dump') else invoice_payload.dict(), 
            workflow_config
        )
        thread_id = initial_state["thread_id"]
        
        # Prepare runtime context
        runtime = {
            "checkpoint_store": checkpoint_store,
            "human_review_repo": human_review_repo
        }
        
        # Run workflow
        config = {"configurable": {"thread_id": thread_id}}
        
        # Execute graph using stream to handle pauses properly
        try:
            # Stream execution and collect state updates
            last_update = None
            for state_update in graph.stream(initial_state, config, stream_mode="updates"):
                last_update = state_update
                # Check if checkpoint created (workflow paused)
                if "checkpoint" in state_update:
                    checkpoint_output = state_update["checkpoint"]
                    if checkpoint_output.get("paused_reason"):
                        checkpoint_id = checkpoint_output.get("cp_id") or final_state_dict.get("hitl_checkpoint_id") if 'final_state_dict' in locals() else None
                        if not checkpoint_id:
                            # Get from state
                            state_snapshot = graph.get_state(config)
                            if state_snapshot:
                                checkpoint_id = state_snapshot.values.get("hitl_checkpoint_id")
                        review_url = checkpoint_output.get("review_url")
                        
                        return WorkflowRunResponse(
                            thread_id=thread_id,
                            status="PAUSED",
                            checkpoint_id=checkpoint_id,
                            review_url=review_url,
                            message="Workflow paused for human review"
                        )
            
            # Get final state after streaming
            final_state_snapshot = graph.get_state(config)
            if final_state_snapshot:
                final_values = final_state_snapshot.values
                
                # Check if paused
                if final_values.get("paused"):
                    checkpoint_output = final_values.get("checkpoint", {})
                    checkpoint_id = checkpoint_output.get("cp_id") or final_values.get("hitl_checkpoint_id")
                    review_url = checkpoint_output.get("review_url")
                    
                    return WorkflowRunResponse(
                        thread_id=thread_id,
                        status="PAUSED",
                        checkpoint_id=checkpoint_id,
                        review_url=review_url,
                        message="Workflow paused for human review"
                    )
                
                # Check if complete
                if final_values.get("complete"):
                    complete_output = final_values.get("complete", {})
                    status = complete_output.get("status", "COMPLETED")
                    
                    return WorkflowRunResponse(
                        thread_id=thread_id,
                        status=status,
                        message="Workflow completed successfully"
                    )
            
            # Still in progress
            return WorkflowRunResponse(
                thread_id=thread_id,
                status="IN_PROGRESS",
                message="Workflow in progress"
            )
        except Exception as e:
            import traceback
            error_detail = f"{str(e)}\n{traceback.format_exc()}"
            raise HTTPException(status_code=500, detail=error_detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/human-review/pending", response_model=PendingReviewsResponse)
async def get_pending_reviews():
    """
    Get all pending human reviews.
    
    Only returns reviews that are:
    - In human_review_queue with decision IS NULL (not yet reviewed)
    - AND workflow status is PAUSED (actually waiting for review)
    - Excludes completed workflows even if decision is NULL in DB
    
    Returns:
        List of pending review items
    """
    try:
        # Get all entries from repo that have no decision in DB
        all_candidates = human_review_repo.get_pending_reviews()
        
        # Filter to only include entries that are actually paused (not completed)
        truly_pending = []
        for item in all_candidates:
            thread_id = item.get("thread_id")
            if not thread_id:
                # No thread_id, skip it (can't verify state)
                continue
                
            try:
                # Check workflow state to see if it's actually paused
                config = {"configurable": {"thread_id": thread_id}}
                state_snapshot = graph.get_state(config)
                if not state_snapshot:
                    # No state found, skip it
                    continue
                    
                state_values = state_snapshot.values
                workflow_status = state_values.get("workflow_status", "UNKNOWN")
                is_paused = state_values.get("paused", False)
                
                # Check if decision exists in state (even if not in DB)
                hitl_output = state_values.get("hitl", {})
                decision_in_state = None
                if hitl_output and isinstance(hitl_output, dict):
                    decision_in_state = hitl_output.get("human_decision")
                
                # Only include if:
                # 1. Status is PAUSED (or paused flag is true)
                # 2. Status is NOT COMPLETED
                # 3. No decision in state (if decision exists in state, it's been reviewed)
                if (is_paused or workflow_status == "PAUSED") and \
                   workflow_status != "COMPLETED" and \
                   not decision_in_state:
                    truly_pending.append(item)
                # Otherwise skip it (completed or already decided)
                    
            except Exception as e:
                # If we can't get state, skip it (safer than showing wrong data)
                # Log the error but don't include the item
                import structlog
                logger = structlog.get_logger()
                logger.warning("Could not verify state for pending review", 
                             thread_id=thread_id, 
                             error=str(e))
        
        items = [HumanReviewItem(**item) for item in truly_pending]
        return PendingReviewsResponse(items=items)
    except Exception as e:
        import traceback
        raise HTTPException(status_code=500, detail=f"{str(e)}\n{traceback.format_exc()}")


@app.post("/human-review/decision", response_model=HumanDecisionResponse)
async def submit_human_decision(
    decision_request: HumanDecisionRequest,
    background_tasks: BackgroundTasks
):
    """
    Submit human decision and resume workflow.
    
    Args:
        decision_request: Human decision request
        background_tasks: Background tasks
        
    Returns:
        Human decision response
    """
    try:
        checkpoint_id = decision_request.checkpoint_id
        
        # Get checkpoint
        checkpoint = human_review_repo.get_checkpoint(checkpoint_id)
        if not checkpoint:
            raise HTTPException(status_code=404, detail="Checkpoint not found")
        
        if checkpoint.get("decision"):
            raise HTTPException(status_code=400, detail="Checkpoint already processed")
        
        thread_id = checkpoint.get("thread_id")
        if not thread_id:
            raise HTTPException(status_code=400, detail="No thread_id in checkpoint")
        
        # Auto-generate reviewer_id if not provided
        reviewer_id = decision_request.reviewer_id or f"reviewer_{uuid.uuid4().hex[:8]}"
        
        # Update decision in repository
        human_review_repo.update_decision(
            checkpoint_id,
            decision_request.decision.upper(),
            reviewer_id,
            decision_request.notes
        )
        
        # Determine next stage
        if decision_request.decision.upper() == "ACCEPT":
            next_stage = "RECONCILE"
        else:
            next_stage = "COMPLETE"
        
        # Get current state from checkpoint
        config = {"configurable": {"thread_id": thread_id}}
        current_state_snapshot = graph.get_state(config)
        if not current_state_snapshot:
            raise HTTPException(status_code=404, detail="Workflow state not found")
        
        # Store human decision in runtime context for HITL_DECISION node
        from src.graph.node_wrapper import runtime_context
        runtime_context.set_human_decision(thread_id, {
            "decision": decision_request.decision.upper(),
            "reviewer_id": reviewer_id,
            "notes": decision_request.notes
        })
        
        # Get current state values
        current_state = current_state_snapshot.values
        
        # Update state with human decision (for HITL_DECISION node)
        # Merge with current state to preserve all data
        state_update = {
            **current_state,  # Preserve existing state
            "hitl": {
                "human_decision": decision_request.decision.upper(),
                "reviewer_id": reviewer_id,  # Use auto-generated or provided reviewer_id
                "resume_token": f"{thread_id}:{checkpoint_id}",
                "next_stage": next_stage
            },
            "paused": False,
            "workflow_status": "IN_PROGRESS"
        }
        
        # Update the state first
        graph.update_state(config, state_update)
        
        # Continue execution - stream from current checkpoint
        # The graph will process HITL_DECISION and continue based on the decision
        final_values = None
        for state_update_stream in graph.stream(None, config, stream_mode="updates"):
            final_values = state_update_stream
        
        # If ACCEPT, continue to complete the workflow
        if decision_request.decision.upper() == "ACCEPT":
            # Continue streaming to complete remaining stages
            for state_update_stream in graph.stream(None, config, stream_mode="updates"):
                final_values = state_update_stream
        
        log_resume_event(thread_id, "CHECKPOINT_HITL", next_stage, checkpoint_id)
        
        resume_token = f"{thread_id}:{checkpoint_id}"
        
        return HumanDecisionResponse(
            resume_token=resume_token,
            next_stage=next_stage,
            message=f"Workflow resumed to {next_stage}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/workflow/{thread_id}")
async def delete_workflow(thread_id: str):
    """
    Delete a workflow by thread_id.
    
    This removes:
    - Workflow state from LangGraph checkpointer
    - Entry from human_review_queue if present
    
    Args:
        thread_id: Workflow thread ID
        
    Returns:
        Success message
    """
    try:
        import sqlite3
        
        # Delete from human_review_queue
        conn = sqlite3.connect("./demo.db")
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM human_review_queue
            WHERE thread_id = ?
        """, (thread_id,))
        
        # Delete from LangGraph checkpoints
        cursor.execute("""
            DELETE FROM checkpoints
            WHERE thread_id = ? AND checkpoint_ns = ''
        """, (thread_id,))
        
        conn.commit()
        conn.close()
        
        return {"message": f"Workflow {thread_id} deleted successfully"}
    except Exception as e:
        import traceback
        raise HTTPException(status_code=500, detail=f"{str(e)}\n{traceback.format_exc()}")


@app.get("/workflow/status/{thread_id}")
async def get_workflow_status(thread_id: str):
    """
    Get workflow status by thread ID.
    
    Args:
        thread_id: Workflow thread ID
        
    Returns:
        Workflow status
    """
    try:
        config = {"configurable": {"thread_id": thread_id}}
        state_snapshot = graph.get_state(config)
        
        if not state_snapshot:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        values = state_snapshot.values
        return {
            "thread_id": thread_id,
            "status": values.get("workflow_status", "UNKNOWN"),
            "current_stage": values.get("current_stage"),
            "paused": values.get("paused", False),
            "complete": values.get("complete") is not None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/workflow/all")
async def get_all_workflows():
    """
    Get all workflows/invoices from the database.
    
    This includes:
    - Workflows that went through HITL (from human_review_queue)
    - Workflows that auto-completed (from LangGraph checkpointer only)
    
    Returns:
        List of all workflows with their details
    """
    try:
        import sqlite3
        
        workflows = []
        seen_thread_ids = set()  # Track thread_ids we've already processed
        
        # Step 1: Get workflows from human_review_queue (HITL workflows)
        conn = sqlite3.connect("./demo.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='human_review_queue'
        """)
        
        if cursor.fetchone():
            cursor.execute("""
                SELECT checkpoint_id, invoice_id, vendor_name, amount, 
                       created_at, reason_for_hold, mismatch_reason, failed_stage,
                       decision, reviewer_id, notes, updated_at, thread_id
                FROM human_review_queue
            """)
            
            checkpoints = cursor.fetchall()
            
            # Process HITL workflows
            for row in checkpoints:
                checkpoint = dict(row)
                thread_id = checkpoint.get("thread_id")
                
                if thread_id:
                    seen_thread_ids.add(thread_id)
                    workflow = await _get_workflow_from_thread_id(thread_id, checkpoint)
                    if workflow:
                        workflows.append(workflow)
        
        # Step 2: Get all workflows from LangGraph checkpointer
        # This includes auto-completed workflows that never hit HITL
        try:
            # Get all checkpoints from LangGraph's SQLite checkpointer
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='checkpoints'
            """)
            
            if cursor.fetchone():
                cursor.execute("""
                    SELECT DISTINCT thread_id, checkpoint_ns
                    FROM checkpoints
                    WHERE checkpoint_ns = ''
                    ORDER BY checkpoint_ns, thread_id
                """)
                
                all_thread_ids = cursor.fetchall()
                
                for row in all_thread_ids:
                    thread_id = row["thread_id"]
                    
                    # Skip if we already processed this thread_id from human_review_queue
                    if thread_id in seen_thread_ids:
                        continue
                    
                    # Get workflow state for this thread_id
                    workflow = await _get_workflow_from_thread_id(thread_id, None)
                    if workflow:
                        workflows.append(workflow)
        except Exception as e:
            # If checkpoints table doesn't exist or query fails, continue
            import structlog
            logger = structlog.get_logger()
            logger.warning("Could not query LangGraph checkpoints", error=str(e))
        
        conn.close()
        
        return {"workflows": workflows, "total": len(workflows)}
    except Exception as e:
        import traceback
        raise HTTPException(status_code=500, detail=f"{str(e)}\n{traceback.format_exc()}")


async def _get_workflow_from_thread_id(thread_id: str, checkpoint_row: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Get workflow data from a thread_id.
    
    Args:
        thread_id: Workflow thread ID
        checkpoint_row: Optional row from human_review_queue table
        
    Returns:
        Workflow dict or None
    """
    try:
        config = {"configurable": {"thread_id": thread_id}}
        state_snapshot = graph.get_state(config)
        
        if not state_snapshot:
            return None
        
        state_values = state_snapshot.values
        
        # Get invoice data from state
        invoice_payload = state_values.get("invoice_payload", {})
        invoice_id = invoice_payload.get("invoice_id") if invoice_payload else None
        vendor_name = invoice_payload.get("vendor_name") if invoice_payload else None
        amount = invoice_payload.get("amount") if invoice_payload else None
        
        # Use checkpoint_row data if available, otherwise extract from state
        if checkpoint_row:
            invoice_id = checkpoint_row.get("invoice_id") or invoice_id
            vendor_name = checkpoint_row.get("vendor_name") or vendor_name
            amount = checkpoint_row.get("amount") or amount
            created_at = checkpoint_row.get("created_at")
            checkpoint_id = checkpoint_row.get("checkpoint_id")
        else:
            # Extract from state or use defaults
            created_at = state_values.get("intake", {}).get("ingest_ts") if state_values.get("intake") else None
            checkpoint_id = None
        
        # Get decision from state if available
        hitl_output = state_values.get("hitl", {})
        decision_from_state = None
        reviewer_id_from_state = None
        
        if hitl_output and isinstance(hitl_output, dict):
            decision_from_state = hitl_output.get("human_decision")
            reviewer_id_from_state = hitl_output.get("reviewer_id")
        
        # Prioritize database values over state (database is the source of truth after human decision)
        # This ensures that if database was updated, we use the updated values
        if checkpoint_row:
            decision = checkpoint_row.get("decision") or decision_from_state
            reviewer_id = checkpoint_row.get("reviewer_id") or reviewer_id_from_state
        elif decision_from_state:
            decision = decision_from_state
            reviewer_id = reviewer_id_from_state
        else:
            decision = None
            reviewer_id = None
        
        # Determine if this workflow went through HITL
        went_through_hitl = False
        if checkpoint_row:
            went_through_hitl = checkpoint_row.get("reason_for_hold") == "MATCH_FAILED_HITL"
        else:
            # Check if there's a checkpoint stage output
            checkpoint_output = state_values.get("checkpoint", {})
            if checkpoint_output and checkpoint_output.get("cp_id"):
                went_through_hitl = True
        
        workflow_status = state_values.get("workflow_status", "UNKNOWN")
        
        return {
            "checkpoint_id": checkpoint_id,
            "invoice_id": invoice_id,
            "thread_id": thread_id,
            "vendor_name": vendor_name,
            "amount": amount,
            "status": workflow_status,
            "paused": state_values.get("paused", False),
            "current_stage": state_values.get("current_stage"),
            "created_at": created_at,
            "decision": decision,
            "reviewer_id": reviewer_id,
            "reason_for_hold": checkpoint_row.get("reason_for_hold") if checkpoint_row else None,
            "went_through_hitl": went_through_hitl,
            "notes": checkpoint_row.get("notes") if checkpoint_row else None,
            "updated_at": checkpoint_row.get("updated_at") if checkpoint_row else None,
            "stages": {
                "intake": state_values.get("intake"),
                "understand": state_values.get("understand"),
                "prepare": state_values.get("prepare"),
                "retrieve": state_values.get("retrieve"),
                "match_two_way": state_values.get("match_two_way"),
                "checkpoint": state_values.get("checkpoint"),
                "hitl": state_values.get("hitl"),
                "reconcile": state_values.get("reconcile"),
                "approve": state_values.get("approve"),
                "posting": state_values.get("posting"),
                "notify": state_values.get("notify"),
                "complete": state_values.get("complete")
            },
            "invoice_payload": invoice_payload
        }
    except Exception as e:
        # If we can't get state, return basic info if checkpoint_row exists
        if checkpoint_row:
            return {
                "checkpoint_id": checkpoint_row.get("checkpoint_id"),
                "invoice_id": checkpoint_row.get("invoice_id"),
                "thread_id": thread_id,
                "vendor_name": checkpoint_row.get("vendor_name"),
                "amount": checkpoint_row.get("amount"),
                "status": "UNKNOWN",
                "created_at": checkpoint_row.get("created_at"),
                "decision": checkpoint_row.get("decision"),
                "reviewer_id": checkpoint_row.get("reviewer_id"),
                "reason_for_hold": checkpoint_row.get("reason_for_hold"),
                "went_through_hitl": checkpoint_row.get("reason_for_hold") == "MATCH_FAILED_HITL"
            }
        # Log error but return None to continue processing other workflows
        import structlog
        logger = structlog.get_logger()
        logger.warning("Could not get workflow from thread_id", thread_id=thread_id, error=str(e))
        return None


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
