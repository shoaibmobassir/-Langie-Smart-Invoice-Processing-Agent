"""LangGraph builder for invoice processing workflow."""

import uuid
from datetime import datetime
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from src.state.models import WorkflowState, WorkflowStatus
from src.config.workflow_loader import WorkflowConfigLoader
from src.storage.checkpoint_store import CheckpointStore
from src.storage.human_review_repo import HumanReviewRepository
from src.graph.routing import route_after_match, route_after_hitl, should_checkpoint
from src.graph.node_wrapper import runtime_context, wrap_node
from src.nodes import (
    intake, understand, prepare, retrieve, match_two_way,
    checkpoint_hitl, hitl_decision, reconcile, approve,
    posting, notify, complete
)


def build_invoice_graph(config_path: str = None) -> tuple[StateGraph, CheckpointStore, HumanReviewRepository]:
    """
    Build LangGraph invoice processing workflow.
    
    Args:
        config_path: Path to workflow.json (optional)
        
    Returns:
        Tuple of (graph, checkpointer, human_review_repo)
    """
    # Load workflow config
    loader = WorkflowConfigLoader(config_path)
    workflow_config = loader.get_config()
    
    # Initialize checkpoint store
    db_path = workflow_config.get("default_db", "sqlite:///./demo.db")
    checkpoint_store = CheckpointStore(db_path)
    checkpointer = checkpoint_store.get_checkpointer()
    
    # Initialize human review repository
    db_path_clean = db_path.replace("sqlite:///", "")
    human_review_repo = HumanReviewRepository(db_path_clean)
    
    # Set runtime context for nodes
    runtime_context.set(checkpoint_store, human_review_repo)
    
    # Create state graph
    graph = StateGraph(WorkflowState)
    
    # Add all nodes (wrap nodes that need runtime context)
    graph.add_node("INTAKE", wrap_node(intake.intake_node, inject_runtime=True))
    graph.add_node("UNDERSTAND", wrap_node(understand.understand_node, inject_runtime=True))
    graph.add_node("PREPARE", wrap_node(prepare.prepare_node, inject_runtime=True))
    graph.add_node("RETRIEVE", wrap_node(retrieve.retrieve_node, inject_runtime=True))
    graph.add_node("MATCH_TWO_WAY", wrap_node(match_two_way.match_two_way_node, inject_runtime=True))
    graph.add_node("CHECKPOINT_HITL", wrap_node(checkpoint_hitl.checkpoint_hitl_node, inject_runtime=True))
    graph.add_node("HITL_DECISION", wrap_node(hitl_decision.hitl_decision_node, inject_runtime=True))
    graph.add_node("RECONCILE", wrap_node(reconcile.reconcile_node, inject_runtime=True))
    graph.add_node("APPROVE", wrap_node(approve.approve_node, inject_runtime=True))
    graph.add_node("POSTING", wrap_node(posting.posting_node, inject_runtime=True))
    graph.add_node("NOTIFY", wrap_node(notify.notify_node, inject_runtime=True))
    graph.add_node("COMPLETE", wrap_node(complete.complete_node, inject_runtime=True))
    
    # Define edges
    graph.set_entry_point("INTAKE")
    
    # Sequential flow
    graph.add_edge("INTAKE", "UNDERSTAND")
    graph.add_edge("UNDERSTAND", "PREPARE")
    graph.add_edge("PREPARE", "RETRIEVE")
    graph.add_edge("RETRIEVE", "MATCH_TWO_WAY")
    
    # Conditional routing after match
    graph.add_conditional_edges(
        "MATCH_TWO_WAY",
        route_after_match,
        {
            "CHECKPOINT_HITL": "CHECKPOINT_HITL",
            "RECONCILE": "RECONCILE"
        }
    )
    
    # After checkpoint, go to HITL_DECISION
    # HITL_DECISION will check for human decision and route accordingly
    graph.add_edge("CHECKPOINT_HITL", "HITL_DECISION")
    
    # Entry point for resuming after checkpoint (from API)
    # HITL_DECISION can be entered directly when resuming
    graph.add_conditional_edges(
        "HITL_DECISION",
        route_after_hitl,
        {
            "RECONCILE": "RECONCILE",
            "COMPLETE": "COMPLETE",
            "__end__": END
        }
    )
    
    # Continue flow after RECONCILE (whether from match or HITL)
    graph.add_edge("RECONCILE", "APPROVE")
    graph.add_edge("APPROVE", "POSTING")
    graph.add_edge("POSTING", "NOTIFY")
    graph.add_edge("NOTIFY", "COMPLETE")
    graph.add_edge("COMPLETE", END)
    
    # Compile graph with checkpointer
    compiled_graph = graph.compile(checkpointer=checkpointer)
    
    return compiled_graph, checkpoint_store, human_review_repo


def create_initial_state(invoice_payload: Dict[str, Any], config: Dict[str, Any]) -> WorkflowState:
    """
    Create initial workflow state.
    
    Args:
        invoice_payload: Invoice payload
        config: Workflow configuration
        
    Returns:
        Initial workflow state
    """
    thread_id = str(uuid.uuid4())
    
    return WorkflowState(
        config=config,
        invoice_payload=invoice_payload,
        paused=False,
        paused_reason=None,
        hitl_checkpoint_id=None,
        thread_id=thread_id,
        current_stage="INTAKE",
        resume_token=None,
        intake=None,
        understand=None,
        prepare=None,
        retrieve=None,
        match_two_way=None,
        checkpoint=None,
        hitl=None,
        reconcile=None,
        approve=None,
        posting=None,
        notify=None,
        complete=None,
        workflow_status=WorkflowStatus.PENDING.value,
        created_at=datetime.utcnow().isoformat(),
        updated_at=None,
        error=None
    )

