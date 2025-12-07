"""Demo run script for Langie invoice processing workflow."""

import asyncio
import json
from datetime import datetime, timedelta
from src.graph.builder import build_invoice_graph, create_initial_state
from src.config.workflow_loader import WorkflowConfigLoader


def create_sample_invoice_pass():
    """Create sample invoice that will pass matching."""
    return {
        "invoice_id": "INV-2024-001",
        "vendor_name": "Acme Corporation",
        "vendor_tax_id": "TAX-123456",
        "invoice_date": "2024-01-15",
        "due_date": "2024-02-15",
        "amount": 1000.00,
        "currency": "USD",
        "line_items": [
            {
                "desc": "Widget A",
                "qty": 10,
                "unit_price": 50.00,
                "total": 500.00
            },
            {
                "desc": "Widget B",
                "qty": 5,
                "unit_price": 100.00,
                "total": 500.00
            }
        ],
        "attachments": ["invoice_001.pdf"]
    }


def create_sample_invoice_fail():
    """Create sample invoice that will fail matching."""
    return {
        "invoice_id": "INV-2024-002",
        "vendor_name": "Beta Industries",
        "vendor_tax_id": "TAX-789012",
        "invoice_date": "2024-01-20",
        "due_date": "2024-02-20",
        "amount": 5000.00,
        "currency": "USD",
        "line_items": [
            {
                "desc": "Unknown Item",
                "qty": 100,
                "unit_price": 60.00,
                "total": 6000.00  # Different from PO amount
            }
        ],
        "attachments": ["invoice_002.pdf"]
    }


async def run_workflow_demo(invoice_payload, description):
    """Run workflow demo with given invoice."""
    print(f"\n{'='*60}")
    print(f"Demo: {description}")
    print(f"{'='*60}\n")
    
    # Load config
    loader = WorkflowConfigLoader()
    config = loader.get_config()
    
    # Build graph
    graph, checkpoint_store, human_review_repo = build_invoice_graph()
    
    # Create initial state
    initial_state = create_initial_state(invoice_payload, config)
    thread_id = initial_state["thread_id"]
    
    print(f"Thread ID: {thread_id}")
    print(f"Invoice ID: {invoice_payload['invoice_id']}")
    print(f"Vendor: {invoice_payload['vendor_name']}")
    print(f"Amount: ${invoice_payload['amount']}\n")
    
    # Run workflow
    config_dict = {"configurable": {"thread_id": thread_id}}
    
    print("Executing workflow stages...\n")
    
    try:
        for state_update in graph.stream(initial_state, config_dict, stream_mode="updates"):
            for stage_name, stage_output in state_update.items():
                print(f"✓ {stage_name}")
                if isinstance(stage_output, dict):
                    # Print key outputs
                    if "paused" in stage_output and stage_output["paused"]:
                        print(f"  ⏸️  Workflow PAUSED for human review")
                        checkpoint_id = stage_output.get("checkpoint_id")
                        if checkpoint_id:
                            print(f"  📋 Checkpoint ID: {checkpoint_id}")
        
        # Get final state
        final_state = graph.get_state(config_dict)
        if final_state:
            values = final_state.values
            workflow_status = values.get("workflow_status", "UNKNOWN")
            
            print(f"\n{'='*60}")
            print(f"Final Status: {workflow_status}")
            print(f"{'='*60}\n")
            
            if values.get("complete"):
                complete_output = values["complete"]
                final_payload = complete_output.get("final_payload", {})
                print("Final Payload Summary:")
                print(json.dumps(final_payload, indent=2, default=str))
            
            if values.get("paused"):
                print("\n⚠️  Workflow is paused. Use the API to submit human decision.")
                pending = human_review_repo.get_pending_reviews()
                if pending:
                    print(f"\nPending Reviews: {len(pending)}")
                    for review in pending:
                        print(f"  - {review['invoice_id']}: {review['vendor_name']} (${review['amount']})")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run demo scenarios."""
    print("🧾 Langie - Invoice Processing Workflow Demo")
    print("=" * 60)
    
    # Demo 1: Invoice that passes matching (no HITL)
    invoice_pass = create_sample_invoice_pass()
    asyncio.run(run_workflow_demo(invoice_pass, "Invoice with Successful Match (No HITL)"))
    
    # Demo 2: Invoice that fails matching (triggers HITL)
    invoice_fail = create_sample_invoice_fail()
    asyncio.run(run_workflow_demo(invoice_fail, "Invoice with Failed Match (Triggers HITL)"))
    
    print("\n" + "="*60)
    print("Demo completed!")
    print("="*60)
    print("\nTo test HITL workflow:")
    print("1. Start the FastAPI server: python -m src.api.app")
    print("2. Submit an invoice via the frontend")
    print("3. Go to Human Review page to accept/reject")
    print("4. Workflow will resume based on decision")


if __name__ == "__main__":
    main()

