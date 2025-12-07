#!/usr/bin/env python3
"""
Populate database with sample data by running test workflows.

This script:
1. Clears/resets the database
2. Submits various invoice scenarios
3. Populates the database with workflows for demonstration
"""

import sys
import os
import json
import time
import requests
import uuid
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

API_BASE = "http://localhost:8000"

# Colors for output
class Colors:
    OKGREEN = '\033[92m'
    OKBLUE = '\033[94m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.OKBLUE}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.OKBLUE}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.OKBLUE}{'='*70}{Colors.ENDC}\n")

def print_success(msg):
    print(f"{Colors.OKGREEN}✅ {msg}{Colors.ENDC}")

def print_info(msg):
    print(f"{Colors.OKBLUE}ℹ️  {msg}{Colors.ENDC}")

def print_error(msg):
    print(f"{Colors.FAIL}❌ {msg}{Colors.ENDC}")

def print_warning(msg):
    print(f"{Colors.WARNING}⚠️  {msg}{Colors.ENDC}")

def check_api():
    """Check if API is running."""
    try:
        response = requests.get(f"{API_BASE}/docs", timeout=3)
        return response.status_code in [200, 404]  # 404 is OK, means server is running
    except:
        return False

def clear_database():
    """Clear existing database files."""
    db_files = ["demo.db", "demo.db-shm", "demo.db-wal"]
    cleared = []
    for db_file in db_files:
        if os.path.exists(db_file):
            try:
                os.remove(db_file)
                cleared.append(db_file)
            except Exception as e:
                print_error(f"Could not delete {db_file}: {e}")
    
    if cleared:
        print_success(f"Cleared database files: {', '.join(cleared)}")
    else:
        print_info("No existing database files to clear")

def submit_invoice(invoice_data, description=""):
    """Submit an invoice via API."""
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
            result = response.json()
            print_success(f"Submitted: {invoice_data.get('invoice_id')} - {description}")
            return result
        else:
            print_error(f"Failed: {invoice_data.get('invoice_id')} - {response.status_code}")
            return None
    except Exception as e:
        print_error(f"Error submitting {invoice_data.get('invoice_id')}: {e}")
        return None

def wait_for_completion(thread_id, timeout=10):
    """Wait for workflow to complete or pause."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{API_BASE}/workflow/status/{thread_id}", timeout=3)
            if response.status_code == 200:
                status = response.json()
                workflow_status = status.get("status", "UNKNOWN")
                if workflow_status in ["COMPLETED", "PAUSED"]:
                    return status
            time.sleep(1)
        except:
            time.sleep(1)
    return None

def get_all_workflows():
    """Get all workflows from database."""
    try:
        response = requests.get(f"{API_BASE}/workflow/all", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("workflows", [])
        return []
    except:
        return []

def main():
    """Main function to populate database."""
    print_header("Database Population Script")
    
    # Check API
    print_info("Checking if backend API is running...")
    if not check_api():
        print_error("Backend API is not running!")
        print_info("Please start the backend first:")
        print_info("  ./start_backend.sh")
        print_info("  OR")
        print_info("  /Users/shoaibmobassir/miniconda3/bin/python -m uvicorn src.api.app:app --host 0.0.0.0 --port 8000")
        sys.exit(1)
    
    print_success("Backend API is running")
    
    # Check if we should clear database (via command line arg)
    clear_db = "--clear" in sys.argv or "-c" in sys.argv
    
    print_header("Checking Database State")
    
    workflows = get_all_workflows()
    if workflows and clear_db:
        print_info(f"Found {len(workflows)} existing workflows. Clearing database (--clear flag set)...")
        print_info("Note: Please restart backend after clearing, then run script again without --clear")
        clear_database()
        sys.exit(0)
    elif workflows:
        print_info(f"Found {len(workflows)} existing workflows. Will add new workflows to existing data.")
    else:
        print_info("Database is empty or freshly initialized. Proceeding with population.")
    
    # Load test invoices
    print_header("Loading Test Scenarios")
    
    test_invoices = []
    
    # Scenario 1: Auto-complete (perfect match)
    test_invoices.append({
        "data": {
            "invoice_id": "INV-SAMPLE-001",
            "vendor_name": "Acme Corp",
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
            "attachments": []
        },
        "description": "Auto-complete (perfect match)"
    })
    
    # Scenario 2: Auto-complete (within tolerance)
    test_invoices.append({
        "data": {
            "invoice_id": "INV-SAMPLE-002",
            "vendor_name": "Acme Corp",
            "vendor_tax_id": "TAX-123456",
            "invoice_date": "2024-01-16",
            "due_date": "2024-02-16",
            "amount": 1005.00,
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
                    "unit_price": 101.00,
                    "total": 505.00
                }
            ],
            "attachments": []
        },
        "description": "Auto-complete (within tolerance: +$5)"
    })
    
    # Scenario 3: HITL trigger (match fails)
    test_invoices.append({
        "data": {
            "invoice_id": "INV-SAMPLE-003",
            "vendor_name": "Beta Industries",
            "vendor_tax_id": "TAX-789012",
            "invoice_date": "2024-01-20",
            "due_date": "2024-02-20",
            "amount": 6000.00,
            "currency": "USD",
            "line_items": [
                {
                    "desc": "Unknown Item",
                    "qty": 100,
                    "unit_price": 60.00,
                    "total": 6000.00
                }
            ],
            "attachments": []
        },
        "description": "HITL trigger (match fails - $6000 vs $1000 PO)"
    })
    
    # Scenario 4: Another auto-complete
    test_invoices.append({
        "data": {
            "invoice_id": "INV-SAMPLE-004",
            "vendor_name": "Acme Corp",
            "vendor_tax_id": "TAX-123456",
            "invoice_date": "2024-01-17",
            "due_date": "2024-02-17",
            "amount": 995.00,
            "currency": "USD",
            "line_items": [
                {
                    "desc": "Widget A",
                    "qty": 10,
                    "unit_price": 49.50,
                    "total": 495.00
                },
                {
                    "desc": "Widget B",
                    "qty": 5,
                    "unit_price": 100.00,
                    "total": 500.00
                }
            ],
            "attachments": []
        },
        "description": "Auto-complete (within tolerance: -$5)"
    })
    
    # Scenario 5: Another HITL trigger
    test_invoices.append({
        "data": {
            "invoice_id": "INV-SAMPLE-005",
            "vendor_name": "Gamma Corp",
            "vendor_tax_id": "TAX-345678",
            "invoice_date": "2024-01-25",
            "due_date": "2024-02-25",
            "amount": 17500.00,
            "currency": "USD",
            "line_items": [
                {
                    "desc": "Premium Service",
                    "qty": 50,
                    "unit_price": 350.00,
                    "total": 17500.00
                }
            ],
            "attachments": []
        },
        "description": "HITL trigger (large amount, no matching PO)"
    })
    
    # Scenario 6: Auto-complete (at tolerance boundary)
    test_invoices.append({
        "data": {
            "invoice_id": "INV-SAMPLE-006",
            "vendor_name": "Acme Corp",
            "vendor_tax_id": "TAX-123456",
            "invoice_date": "2024-01-18",
            "due_date": "2024-02-18",
            "amount": 1050.00,
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
                    "unit_price": 110.00,
                    "total": 550.00
                }
            ],
            "attachments": []
        },
        "description": "Auto-complete (at tolerance boundary: +$50, 5%)"
    })
    
    # Scenario 7: Auto-complete (single line item)
    test_invoices.append({
        "data": {
            "invoice_id": "INV-SAMPLE-007",
            "vendor_name": "Acme Corp",
            "vendor_tax_id": "TAX-123456",
            "invoice_date": "2024-01-19",
            "due_date": "2024-02-19",
            "amount": 500.00,
            "currency": "USD",
            "line_items": [
                {
                    "desc": "Widget A",
                    "qty": 10,
                    "unit_price": 50.00,
                    "total": 500.00
                }
            ],
            "attachments": []
        },
        "description": "Auto-complete (single line item - partial PO match)"
    })
    
    # Scenario 8: HITL trigger (vendor mismatch)
    test_invoices.append({
        "data": {
            "invoice_id": "INV-SAMPLE-008",
            "vendor_name": "Delta Industries",
            "vendor_tax_id": "TAX-999999",
            "invoice_date": "2024-01-21",
            "due_date": "2024-02-21",
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
            "attachments": []
        },
        "description": "HITL trigger (amount matches but vendor doesn't match PO)"
    })
    
    # Scenario 9: Auto-complete (quantity variation)
    test_invoices.append({
        "data": {
            "invoice_id": "INV-SAMPLE-009",
            "vendor_name": "Acme Corp",
            "vendor_tax_id": "TAX-123456",
            "invoice_date": "2024-01-22",
            "due_date": "2024-02-22",
            "amount": 1000.00,
            "currency": "USD",
            "line_items": [
                {
                    "desc": "Widget A",
                    "qty": 11,
                    "unit_price": 45.45,
                    "total": 500.00
                },
                {
                    "desc": "Widget B",
                    "qty": 5,
                    "unit_price": 100.00,
                    "total": 500.00
                }
            ],
            "attachments": []
        },
        "description": "Auto-complete (quantity/price variation, same total)"
    })
    
    # Scenario 10: HITL trigger (amount way over)
    test_invoices.append({
        "data": {
            "invoice_id": "INV-SAMPLE-010",
            "vendor_name": "Beta Industries",
            "vendor_tax_id": "TAX-789012",
            "invoice_date": "2024-01-23",
            "due_date": "2024-02-23",
            "amount": 15000.00,
            "currency": "USD",
            "line_items": [
                {
                    "desc": "Bulk Order",
                    "qty": 300,
                    "unit_price": 50.00,
                    "total": 15000.00
                }
            ],
            "attachments": []
        },
        "description": "HITL trigger (amount way over: $15K vs $1K PO)"
    })
    
    # Scenario 11: Auto-complete (small invoice)
    test_invoices.append({
        "data": {
            "invoice_id": "INV-SAMPLE-011",
            "vendor_name": "Acme Corp",
            "vendor_tax_id": "TAX-123456",
            "invoice_date": "2024-01-24",
            "due_date": "2024-02-24",
            "amount": 250.00,
            "currency": "USD",
            "line_items": [
                {
                    "desc": "Widget A",
                    "qty": 5,
                    "unit_price": 50.00,
                    "total": 250.00
                }
            ],
            "attachments": []
        },
        "description": "Auto-complete (small invoice amount)"
    })
    
    # Scenario 12: Auto-complete (vendor name normalization)
    test_invoices.append({
        "data": {
            "invoice_id": "INV-SAMPLE-012",
            "vendor_name": "Acme Corporation",
            "vendor_tax_id": "TAX-123456",
            "invoice_date": "2024-01-26",
            "due_date": "2024-02-26",
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
            "attachments": []
        },
        "description": "Auto-complete (vendor name normalization: 'Acme Corporation' → 'Acme Corp')"
    })
    
    # Scenario 13: HITL trigger (line item mismatch)
    test_invoices.append({
        "data": {
            "invoice_id": "INV-SAMPLE-013",
            "vendor_name": "Acme Corp",
            "vendor_tax_id": "TAX-123456",
            "invoice_date": "2024-01-27",
            "due_date": "2024-02-27",
            "amount": 1000.00,
            "currency": "USD",
            "line_items": [
                {
                    "desc": "Widget C",
                    "qty": 20,
                    "unit_price": 50.00,
                    "total": 1000.00
                }
            ],
            "attachments": []
        },
        "description": "HITL trigger (amount matches but line items don't match PO)"
    })
    
    print_info(f"Loaded {len(test_invoices)} test scenarios")
    
    # Submit invoices
    print_header("Submitting Invoices")
    
    submitted = []
    for idx, invoice_info in enumerate(test_invoices, 1):
        invoice_data = invoice_info["data"]
        description = invoice_info["description"]
        
        print_info(f"[{idx}/{len(test_invoices)}] Submitting {invoice_data.get('invoice_id')}...")
        result = submit_invoice(invoice_data, description)
        
        if result:
            submitted.append({
                "invoice_id": invoice_data.get("invoice_id"),
                "thread_id": result.get("thread_id"),
                "description": description
            })
        
        # Small delay between submissions
        time.sleep(1)
    
    print_header("Waiting for Workflows to Complete")
    
    # Wait for workflows to process
    print_info("Waiting for workflows to complete or pause...")
    time.sleep(5)
    
    # Check status of submitted workflows
    for item in submitted:
        status = wait_for_completion(item["thread_id"], timeout=5)
        if status:
            workflow_status = status.get("status", "UNKNOWN")
            print_info(f"  {item['invoice_id']}: {workflow_status}")
    
    print_header("Processing Human Reviews")
    
    # Get pending reviews and process some
    try:
        response = requests.get(f"{API_BASE}/human-review/pending", timeout=5)
        if response.status_code == 200:
            pending = response.json().get("items", [])
            print_info(f"Found {len(pending)} pending reviews")
            
            # Process first few pending reviews with unique reviewer IDs
            # Mix of ACCEPT and REJECT decisions for variety
            decisions_to_process = ["ACCEPT", "ACCEPT", "REJECT"]
            
            for idx, review in enumerate(pending[:3]):  # Process first 3 pending reviews
                checkpoint_id = review.get("checkpoint_id")
                invoice_id = review.get("invoice_id")
                decision = decisions_to_process[idx] if idx < len(decisions_to_process) else "ACCEPT"
                
                # Generate unique reviewer ID for each review
                reviewer_id = f"demo_reviewer_{uuid.uuid4().hex[:8]}"
                
                print_info(f"[{idx+1}/{min(3, len(pending))}] Submitting {decision} decision for {invoice_id} (Reviewer: {reviewer_id})...")
                
                decision_response = requests.post(
                    f"{API_BASE}/human-review/decision",
                    json={
                        "checkpoint_id": checkpoint_id,
                        "decision": decision,
                        "reviewer_id": reviewer_id,
                        "notes": f"Auto-processed during database population - Decision: {decision}"
                    },
                    timeout=30
                )
                
                if decision_response.status_code == 200:
                    print_success(f"{decision} decision submitted for {invoice_id} - Reviewer: {reviewer_id}")
                else:
                    print_error(f"Failed to submit decision: {decision_response.status_code}")
                
                # Small delay between decisions
                time.sleep(1)
        else:
            print_info("No pending reviews found")
    except Exception as e:
        print_error(f"Error processing reviews: {e}")
    
    # Wait a bit more for workflows to finalize and persist to database
    print_info("Waiting for final workflow processing and database persistence...")
    time.sleep(5)
    
    # Get final database state
    print_header("Database Summary")
    
    workflows = get_all_workflows()
    
    if workflows:
        print_success(f"Database populated with {len(workflows)} workflows")
        print()
        
        # Count by status
        status_counts = {}
        decision_counts = {"ACCEPT": 0, "REJECT": 0, None: 0}
        
        for wf in workflows:
            status = wf.get("status", "UNKNOWN")
            status_counts[status] = status_counts.get(status, 0) + 1
            
            decision = wf.get("decision")
            decision_counts[decision] = decision_counts.get(decision, 0) + 1
        
        print_info("Workflows by Status:")
        for status, count in sorted(status_counts.items()):
            print_info(f"  - {status}: {count}")
        
        print()
        print_info("Workflows by Decision:")
        print_info(f"  - ACCEPT: {decision_counts.get('ACCEPT', 0)}")
        print_info(f"  - REJECT: {decision_counts.get('REJECT', 0)}")
        print_info(f"  - None (Auto-completed): {decision_counts.get(None, 0)}")
        
        print()
        print_info("Sample Workflows:")
        for wf in workflows[:5]:
            invoice_id = wf.get("invoice_id", "N/A")
            status = wf.get("status", "N/A")
            decision = wf.get("decision")
            went_through_hitl = wf.get("went_through_hitl", False)
            
            decision_str = decision if decision else ("No Review Needed" if not went_through_hitl else "Pending")
            print_info(f"  - {invoice_id}: {status} ({decision_str})")
        
        print()
        print_success("✅ Database population complete!")
        print()
        print_info("Next steps:")
        print_info("  1. Open frontend: http://localhost:5173")
        print_info("  2. Go to Database Preview tab")
        print_info("  3. View all populated workflows")
        print_info("  4. Filter by status, sort, and explore details")
    else:
        print_warning("No workflows found in database. Check backend logs for errors.")

if __name__ == "__main__":
    main()

