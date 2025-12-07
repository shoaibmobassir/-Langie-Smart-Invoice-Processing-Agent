#!/usr/bin/env python3
"""
Test script for auto-complete scenarios (no HITL needed).

This script tests invoices that should process automatically without
triggering the Human-In-The-Loop checkpoint.
"""

import json
import sys
import time
import requests
from pathlib import Path
from typing import Dict, Any, List

# Configuration
API_BASE = "http://localhost:8000"
TEST_DATA_FILE = "test_data/invoices_auto_complete.json"

# Colors for output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Print formatted header"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.ENDC}\n")


def print_test_case(num, total, description):
    """Print test case header"""
    print(f"\n{Colors.OKCYAN}[Test {num}/{total}] {description}{Colors.ENDC}")
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


def check_api_health() -> bool:
    """Check if API is running"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def submit_invoice(invoice_data: Dict[str, Any]) -> Dict[str, Any]:
    """Submit an invoice via API"""
    try:
        form_data = {
            "invoice": json.dumps(invoice_data),
            "file_count": "0"
        }
        
        response = requests.post(
            f"{API_BASE}/workflow/run",
            data=form_data,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print_error(f"API returned status {response.status_code}")
            print_error(response.text)
            return None
    except Exception as e:
        print_error(f"Error submitting invoice: {e}")
        return None


def get_workflow_status(thread_id: str) -> Dict[str, Any]:
    """Get workflow status"""
    try:
        response = requests.get(f"{API_BASE}/workflow/status/{thread_id}", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print_error(f"Error getting workflow status: {e}")
        return None


def get_all_workflows() -> List[Dict[str, Any]]:
    """Get all workflows and find the one we just submitted"""
    try:
        response = requests.get(f"{API_BASE}/workflow/all", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("workflows", [])
        return []
    except Exception as e:
        print_error(f"Error getting workflows: {e}")
        return []


def verify_auto_complete(invoice_id: str, thread_id: str, wait_time: int = 5) -> bool:
    """Verify that workflow auto-completed without HITL"""
    print_info("Waiting for workflow to complete...")
    time.sleep(wait_time)
    
    # Check workflow status
    status = get_workflow_status(thread_id)
    if not status:
        print_error("Could not get workflow status")
        return False
    
    workflow_status = status.get("status", "UNKNOWN")
    is_paused = status.get("paused", False)
    current_stage = status.get("current_stage", "UNKNOWN")
    
    print_info(f"Workflow Status: {workflow_status}")
    print_info(f"Paused: {is_paused}")
    print_info(f"Current Stage: {current_stage}")
    
    # Get full workflow details
    workflows = get_all_workflows()
    workflow = None
    for wf in workflows:
        if wf.get("invoice_id") == invoice_id:
            workflow = wf
            break
    
    if not workflow:
        print_error(f"Could not find workflow for invoice {invoice_id}")
        return False
    
    # Verify it's completed
    if workflow_status != "COMPLETED":
        print_error(f"Workflow status is {workflow_status}, expected COMPLETED")
        return False
    
    # Verify it didn't go through HITL
    went_through_hitl = workflow.get("went_through_hitl", False)
    if went_through_hitl:
        print_error("Workflow went through HITL checkpoint (should not have)")
        return False
    
    # Verify no decision (because no HITL)
    decision = workflow.get("decision")
    if decision:
        print_warning(f"Workflow has decision {decision} but didn't go through HITL")
        # This might be OK if it's from a previous run
    
    # Check that it completed all stages
    stages = workflow.get("stages", {})
    if not stages.get("complete"):
        print_error("Workflow completed but no COMPLETE stage output found")
        return False
    
    print_success("Workflow auto-completed successfully (no HITL)")
    print_info(f"Final Status: {workflow_status}")
    print_info(f"Stages completed: {len([k for k in stages.keys() if stages[k]])}")
    
    return True


def test_invoice(invoice_data: Dict[str, Any], test_num: int, total: int) -> bool:
    """Test a single invoice"""
    invoice_id = invoice_data.get("invoice_id", "UNKNOWN")
    description = invoice_data.pop("description", "No description")
    
    print_test_case(test_num, total, f"{invoice_id}: {description}")
    
    # Submit invoice
    print_info(f"Submitting invoice {invoice_id}...")
    result = submit_invoice(invoice_data)
    
    if not result:
        print_error("Failed to submit invoice")
        return False
    
    thread_id = result.get("thread_id")
    if not thread_id:
        print_error("No thread_id returned")
        return False
    
    print_success(f"Invoice submitted successfully")
    print_info(f"Thread ID: {thread_id}")
    
    # Verify auto-complete
    return verify_auto_complete(invoice_id, thread_id)


def main():
    """Main test function"""
    print_header("Auto-Complete Scenario Tests")
    
    print_info("These test cases verify that invoices process automatically")
    print_info("without triggering the Human-In-The-Loop checkpoint.")
    print()
    
    # Check API health
    if not check_api_health():
        print_error("Cannot connect to backend API. Is it running?")
        print_info(f"Start backend with: python3 -m uvicorn src.api.app:app --host 0.0.0.0 --port 8000")
        sys.exit(1)
    
    print_success("Backend API is running")
    print()
    
    # Load test data
    test_data_path = Path(TEST_DATA_FILE)
    if not test_data_path.exists():
        print_error(f"Test data file not found: {TEST_DATA_FILE}")
        sys.exit(1)
    
    with open(test_data_path, 'r') as f:
        invoices = json.load(f)
    
    print_info(f"Loaded {len(invoices)} test cases")
    print()
    
    # Run tests
    passed = 0
    failed = 0
    results = []
    
    for idx, invoice in enumerate(invoices, 1):
        success = test_invoice(invoice, idx, len(invoices))
        results.append({
            "invoice_id": invoice.get("invoice_id"),
            "success": success
        })
        
        if success:
            passed += 1
        else:
            failed += 1
        
        # Small delay between tests
        if idx < len(invoices):
            time.sleep(1)
    
    # Summary
    print_header("Test Results Summary")
    
    print_info(f"Total Tests: {len(invoices)}")
    print_success(f"Passed: {passed}")
    if failed > 0:
        print_error(f"Failed: {failed}")
    
    print()
    
    if failed > 0:
        print_info("Failed Test Cases:")
        for result in results:
            if not result["success"]:
                print_error(f"  - {result['invoice_id']}")
    
    print()
    
    if failed == 0:
        print_success("All auto-complete scenarios passed! 🎉")
        return 0
    else:
        print_error(f"{failed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

