#!/usr/bin/env python3
"""
Complete Demo Workflow for Langie - Invoice Processing Agent
This script demonstrates the full workflow with detailed logging
"""

import sys
import json
import time
import requests
from datetime import datetime
from pathlib import Path

# Configuration
API_BASE = "http://localhost:8000"
FRONTEND_BASE = "http://localhost:5173"

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text):
    """Print formatted header"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.ENDC}\n")


def print_step(step_num, title):
    """Print formatted step"""
    print(f"\n{Colors.OKCYAN}[Step {step_num}] {title}{Colors.ENDC}")
    print(f"{Colors.OKCYAN}{'-'*70}{Colors.ENDC}")


def print_success(message):
    """Print success message"""
    print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")


def print_error(message):
    """Print error message"""
    print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")


def print_info(message):
    """Print info message"""
    print(f"{Colors.OKBLUE}ℹ️  {message}{Colors.ENDC}")


def check_api_health():
    """Check if API is running"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            print_success("Backend API is running")
            return True
        else:
            print_error(f"Backend API returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to backend API. Is it running?")
        print_info(f"Start backend with: python3 -m uvicorn src.api.app:app --host 0.0.0.0 --port 8000")
        return False
    except Exception as e:
        print_error(f"Error checking API health: {e}")
        return False


def submit_invoice(invoice_data, files=None, description=""):
    """Submit an invoice via API"""
    print_info(f"Submitting invoice: {invoice_data.get('invoice_id', 'N/A')}")
    if description:
        print_info(f"Description: {description}")
    
    try:
        form_data = {
            "invoice": json.dumps(invoice_data),
            "file_count": str(len(files) if files else 0)
        }
        
        files_to_send = {}
        if files:
            for idx, file_path in enumerate(files):
                if Path(file_path).exists():
                    files_to_send[f"file_{idx}"] = open(file_path, 'rb')
        
        response = requests.post(
            f"{API_BASE}/workflow/run",
            data=form_data,
            files=files_to_send if files_to_send else None,
            timeout=30
        )
        
        # Close file handles
        for f in files_to_send.values():
            f.close()
        
        if response.status_code == 200:
            result = response.json()
            print_success(f"Invoice submitted successfully")
            print_info(f"Thread ID: {result.get('thread_id', 'N/A')}")
            print_info(f"Status: {result.get('status', 'N/A')}")
            return result
        else:
            print_error(f"Failed to submit invoice: {response.status_code}")
            print_error(response.text)
            return None
    except Exception as e:
        print_error(f"Error submitting invoice: {e}")
        return None


def get_pending_reviews():
    """Get pending human reviews"""
    try:
        response = requests.get(f"{API_BASE}/human-review/pending", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("items", [])
        else:
            print_error(f"Failed to get pending reviews: {response.status_code}")
            return []
    except Exception as e:
        print_error(f"Error getting pending reviews: {e}")
        return []


def submit_decision(checkpoint_id, decision, reviewer_id=None, notes=""):
    """Submit human decision"""
    if not reviewer_id:
        reviewer_id = f"demo_reviewer_{int(time.time())}"
    
    print_info(f"Submitting decision: {decision} for checkpoint {checkpoint_id[:8]}...")
    
    try:
        response = requests.post(
            f"{API_BASE}/human-review/decision",
            json={
                "checkpoint_id": checkpoint_id,
                "decision": decision,
                "reviewer_id": reviewer_id,
                "notes": notes
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print_success(f"Decision submitted: {decision}")
            print_info(f"Next stage: {result.get('next_stage', 'N/A')}")
            return result
        else:
            print_error(f"Failed to submit decision: {response.status_code}")
            print_error(response.text)
            return None
    except Exception as e:
        print_error(f"Error submitting decision: {e}")
        return None


def get_workflow_status(thread_id):
    """Get workflow status"""
    try:
        response = requests.get(f"{API_BASE}/workflow/status/{thread_id}", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print_error(f"Error getting workflow status: {e}")
        return None


def get_all_workflows():
    """Get all workflows"""
    try:
        response = requests.get(f"{API_BASE}/workflow/all", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("workflows", [])
        return []
    except Exception as e:
        print_error(f"Error getting workflows: {e}")
        return []


def demo_scenario_1_auto_complete():
    """Demo Scenario 1: Auto-complete (no HITL)"""
    print_step(1, "Scenario 1: Auto-Complete Workflow (No HITL)")
    
    invoice_data = {
        "invoice_id": "INV-DEMO-001",
        "vendor_name": "Acme Corp",
        "vendor_tax_id": "TAX-123456",
        "invoice_date": "2024-01-15",
        "due_date": "2024-02-15",
        "amount": 1000,
        "currency": "USD",
        "line_items": [
            {
                "desc": "Widget A",
                "qty": 10,
                "unit_price": 50,
                "total": 500
            },
            {
                "desc": "Widget B",
                "qty": 5,
                "unit_price": 100,
                "total": 500
            }
        ],
        "attachments": []
    }
    
    result = submit_invoice(
        invoice_data,
        description="Invoice matches PO - will auto-complete without HITL"
    )
    
    if result:
        thread_id = result.get("thread_id")
        print_info("Waiting for workflow to complete...")
        time.sleep(3)
        
        status = get_workflow_status(thread_id)
        if status:
            print_success(f"Workflow Status: {status.get('status', 'N/A')}")
            print_info(f"Current Stage: {status.get('current_stage', 'N/A')}")
            print_info(f"Paused: {status.get('paused', False)}")
        
        print_success("Scenario 1 completed!")
    else:
        print_error("Scenario 1 failed!")


def demo_scenario_2_hitl():
    """Demo Scenario 2: HITL triggered"""
    print_step(2, "Scenario 2: HITL Triggered (Match Failed)")
    
    invoice_data = {
        "invoice_id": "INV-DEMO-002",
        "vendor_name": "Beta Industries",
        "vendor_tax_id": "TAX-789012",
        "invoice_date": "2024-01-20",
        "due_date": "2024-02-20",
        "amount": 6000,  # Amount doesn't match PO - will trigger HITL
        "currency": "USD",
        "line_items": [
            {
                "desc": "Unknown Item",
                "qty": 100,
                "unit_price": 60,
                "total": 6000
            }
        ],
        "attachments": []
    }
    
    result = submit_invoice(
        invoice_data,
        description="Invoice amount doesn't match PO - will trigger HITL"
    )
    
    if result:
        thread_id = result.get("thread_id")
        print_info("Waiting for workflow to reach HITL checkpoint...")
        time.sleep(3)
        
        status = get_workflow_status(thread_id)
        if status:
            print_success(f"Workflow Status: {status.get('status', 'N/A')}")
            print_info(f"Current Stage: {status.get('current_stage', 'N/A')}")
            print_info(f"Paused: {status.get('paused', False)}")
            
            if status.get("paused"):
                print_success("Workflow paused at HITL checkpoint!")
            else:
                print_warning("Workflow may still be processing...")
        
        # Check pending reviews
        pending = get_pending_reviews()
        print_info(f"Pending reviews: {len(pending)}")
        for review in pending:
            if review.get("invoice_id") == "INV-DEMO-002":
                print_info(f"  - Checkpoint ID: {review.get('checkpoint_id', 'N/A')}")
                print_info(f"  - Reason: {review.get('reason_for_hold', 'N/A')}")
        
        print_success("Scenario 2 completed! Workflow is waiting for human review.")
    else:
        print_error("Scenario 2 failed!")


def demo_scenario_3_human_decision():
    """Demo Scenario 3: Human decision and resume"""
    print_step(3, "Scenario 3: Human Decision & Resume")
    
    # Get pending reviews
    pending = get_pending_reviews()
    
    if not pending:
        print_warning("No pending reviews found. Submit an invoice that triggers HITL first.")
        return
    
    # Use the first pending review
    review = pending[0]
    checkpoint_id = review.get("checkpoint_id")
    invoice_id = review.get("invoice_id")
    
    print_info(f"Processing review for invoice: {invoice_id}")
    print_info(f"Checkpoint ID: {checkpoint_id}")
    
    # Submit ACCEPT decision
    result = submit_decision(
        checkpoint_id,
        "ACCEPT",
        reviewer_id="demo_reviewer_001",
        notes="Demo: Accepting invoice after review"
    )
    
    if result:
        print_info("Waiting for workflow to resume and complete...")
        time.sleep(5)
        
        print_success("Workflow resumed and completed after human acceptance!")
    else:
        print_error("Failed to submit decision!")


def demo_scenario_4_database_preview():
    """Demo Scenario 4: Database preview"""
    print_step(4, "Scenario 4: Database Preview")
    
    workflows = get_all_workflows()
    
    print_info(f"Total workflows in database: {len(workflows)}")
    
    # Count by status
    status_counts = {}
    decision_counts = {"ACCEPT": 0, "REJECT": 0, None: 0}
    
    for wf in workflows:
        status = wf.get("status", "UNKNOWN")
        status_counts[status] = status_counts.get(status, 0) + 1
        
        decision = wf.get("decision")
        decision_counts[decision] = decision_counts.get(decision, 0) + 1
    
    print_info("\nWorkflows by Status:")
    for status, count in status_counts.items():
        print_info(f"  - {status}: {count}")
    
    print_info("\nWorkflows by Decision:")
    print_info(f"  - ACCEPT: {decision_counts.get('ACCEPT', 0)}")
    print_info(f"  - REJECT: {decision_counts.get('REJECT', 0)}")
    print_info(f"  - None: {decision_counts.get(None, 0)}")
    
    print_success("Database preview completed!")


def main():
    """Main demo function"""
    print_header("Langie - Invoice Processing Agent Demo")
    
    print_info("This demo will run through multiple scenarios:")
    print_info("  1. Auto-complete workflow (no HITL)")
    print_info("  2. HITL triggered workflow")
    print_info("  3. Human decision and resume")
    print_info("  4. Database preview")
    print()
    
    # Check API health
    if not check_api_health():
        print_error("Cannot proceed without backend API")
        sys.exit(1)
    
    print()
    input("Press Enter to start the demo...")
    print()
    
    # Run scenarios
    try:
        demo_scenario_1_auto_complete()
        time.sleep(2)
        
        demo_scenario_2_hitl()
        time.sleep(2)
        
        demo_scenario_3_human_decision()
        time.sleep(2)
        
        demo_scenario_4_database_preview()
        
        print_header("Demo Completed Successfully!")
        print_info(f"Frontend UI: {FRONTEND_BASE}")
        print_info(f"Backend API: {API_BASE}/docs")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print_error(f"Demo error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

