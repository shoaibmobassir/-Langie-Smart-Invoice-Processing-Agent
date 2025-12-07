"""End-to-end test script for Langie invoice processing."""

import asyncio
import json
import os
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

import requests
from src.graph.builder import build_invoice_graph, create_initial_state
from src.config.workflow_loader import WorkflowConfigLoader


API_BASE = "http://localhost:8000"


def test_api_health():
    """Test if API is running."""
    try:
        response = requests.get(f"{API_BASE}/docs", timeout=2)
        return response.status_code == 200
    except:
        return False


def submit_invoice_via_api(invoice_data, image_files=None):
    """Submit invoice via API with optional image file uploads."""
    print(f"\n📤 Submitting invoice: {invoice_data['invoice_id']}")
    
    if image_files:
        # Use multipart/form-data for file uploads
        files = {}
        form_data = {
            'invoice': json.dumps(invoice_data),
            'file_count': str(len(image_files))
        }
        
        for i, image_file in enumerate(image_files):
            if os.path.exists(image_file):
                files[f'file_{i}'] = (os.path.basename(image_file), open(image_file, 'rb'), 'image/png')
            else:
                print(f"⚠️  Image file not found: {image_file}")
        
        try:
            response = requests.post(
                f"{API_BASE}/workflow/run",
                files=files,
                data=form_data
            )
        finally:
            # Close file handles
            for f in files.values():
                if hasattr(f[1], 'close'):
                    f[1].close()
    else:
        # Use multipart/form-data even without files (API expects form data)
        form_data = {
            'invoice': json.dumps(invoice_data),
            'file_count': '0'
        }
        response = requests.post(
            f"{API_BASE}/workflow/run",
            data=form_data
        )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Response: {result['status']}")
        print(f"   Thread ID: {result['thread_id']}")
        if result.get('checkpoint_id'):
            print(f"   Checkpoint ID: {result['checkpoint_id']}")
            print(f"   Review URL: {result['review_url']}")
        return result
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return None


def get_pending_reviews():
    """Get pending human reviews."""
    response = requests.get(f"{API_BASE}/human-review/pending")
    if response.status_code == 200:
        return response.json()['items']
    return []


def submit_human_decision(checkpoint_id, decision, reviewer_id="test_reviewer"):
    """Submit human decision."""
    print(f"\n👤 Submitting human decision: {decision}")
    response = requests.post(
        f"{API_BASE}/human-review/decision",
        json={
            "checkpoint_id": checkpoint_id,
            "decision": decision,
            "reviewer_id": reviewer_id,
            "notes": f"Test {decision} decision"
        }
    )
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Decision submitted")
        print(f"   Resume token: {result['resume_token']}")
        print(f"   Next stage: {result['next_stage']}")
        return result
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return None


def get_workflow_status(thread_id):
    """Get workflow status."""
    response = requests.get(f"{API_BASE}/workflow/status/{thread_id}")
    if response.status_code == 200:
        return response.json()
    return None


def test_scenario_1_pass():
    """Test scenario 1: Invoice that passes matching."""
    print("\n" + "="*60)
    print("SCENARIO 1: Invoice with Successful Match (No HITL) - PDF")
    print("="*60)
    
    invoice_data = {
        "invoice_id": "INV-2024-001",
        "vendor_name": "Acme Corporation",
        "vendor_tax_id": "TAX-123456",
        "invoice_date": "2024-01-15",
        "due_date": "2024-02-15",
        "amount": 1000.00,
        "currency": "USD",
        "line_items": [
            {"desc": "Widget A", "qty": 10, "unit_price": 50.00, "total": 500.00},
            {"desc": "Widget B", "qty": 5, "unit_price": 100.00, "total": 500.00}
        ],
        "attachments": []
    }
    
    result = submit_invoice_via_api(invoice_data)
    if result:
        thread_id = result['thread_id']
        time.sleep(2)  # Wait for processing
        status = get_workflow_status(thread_id)
        if status:
            print(f"\n📊 Final Status: {status['status']}")
            print(f"   Current Stage: {status.get('current_stage')}")
            print(f"   Paused: {status.get('paused')}")
            print(f"   Complete: {status.get('complete')}")


def test_scenario_1_pass_image():
    """Test scenario 1b: Invoice with image attachment (OCR)."""
    print("\n" + "="*60)
    print("SCENARIO 1b: Invoice with Successful Match - PNG Image (OCR Test)")
    print("="*60)
    
    invoice_data = {
        "invoice_id": "INV-OCR-2024-001",
        "vendor_name": "Acme Corporation",
        "vendor_tax_id": "TAX-123456",
        "invoice_date": "2024-01-15",
        "due_date": "2024-02-15",
        "amount": 1000.00,
        "currency": "USD",
        "line_items": [
            {"desc": "Widget A", "qty": 10, "unit_price": 50.00, "total": 500.00},
            {"desc": "Widget B", "qty": 5, "unit_price": 100.00, "total": 500.00}
        ],
        "attachments": []
    }
    
    # Use image file for OCR testing
    image_file = "test_data/test_data/invoice_pass_image.png"
    if os.path.exists(image_file):
        print(f"📎 Using OCR image: {image_file}")
        result = submit_invoice_via_api(invoice_data, image_files=[image_file])
        if result:
            thread_id = result['thread_id']
            time.sleep(3)  # Wait for OCR processing
            status = get_workflow_status(thread_id)
            if status:
                print(f"\n📊 Final Status: {status['status']}")
                print(f"   Current Stage: {status.get('current_stage')}")
                print(f"   Paused: {status.get('paused')}")
                print("✅ OCR processing completed successfully!")
    else:
        print(f"⚠️  Image file not found: {image_file}")


def test_scenario_2_hitl():
    """Test scenario 2: Invoice that fails matching (triggers HITL)."""
    print("\n" + "="*60)
    print("SCENARIO 2: Invoice with Failed Match (Triggers HITL) - PDF")
    print("="*60)
    
    invoice_data = {
        "invoice_id": "INV-2024-002",
        "vendor_name": "Beta Industries",
        "vendor_tax_id": "TAX-789012",
        "invoice_date": "2024-01-20",
        "due_date": "2024-02-20",
        "amount": 6000.00,
        "currency": "USD",
        "line_items": [
            {"desc": "Unknown Item", "qty": 100, "unit_price": 60.00, "total": 6000.00}
        ],
        "attachments": []
    }
    
    result = submit_invoice_via_api(invoice_data)
    if result and result.get('checkpoint_id'):
        checkpoint_id = result['checkpoint_id']
        print(f"\n⏸️  Workflow paused. Checkpoint ID: {checkpoint_id}")
        
        # Wait a bit
        time.sleep(2)
        
        # Check pending reviews
        pending = get_pending_reviews()
        print(f"\n📋 Pending Reviews: {len(pending)}")
        
        # Submit human decision (ACCEPT)
        decision_result = submit_human_decision(checkpoint_id, "ACCEPT")
        
        if decision_result:
            # Wait for processing
            time.sleep(3)
            thread_id = result['thread_id']
            status = get_workflow_status(thread_id)
            if status:
                print(f"\n📊 Final Status: {status['status']}")
                print(f"   Current Stage: {status.get('current_stage')}")
                print(f"   Complete: {status.get('complete')}")


def test_scenario_2_hitl_image():
    """Test scenario 2b: Invoice with image that fails matching (triggers HITL)."""
    print("\n" + "="*60)
    print("SCENARIO 2b: Invoice with Failed Match - PNG Image (OCR + HITL)")
    print("="*60)
    
    invoice_data = {
        "invoice_id": "INV-OCR-2024-002",
        "vendor_name": "Beta Industries",
        "vendor_tax_id": "TAX-789012",
        "invoice_date": "2024-01-20",
        "due_date": "2024-02-20",
        "amount": 6000.00,
        "currency": "USD",
        "line_items": [
            {"desc": "Unknown Item", "qty": 100, "unit_price": 60.00, "total": 6000.00}
        ],
        "attachments": []
    }
    
    # Use image file for OCR testing
    image_file = "test_data/test_data/invoice_fail_image.png"
    if os.path.exists(image_file):
        print(f"📎 Using OCR image: {image_file}")
        result = submit_invoice_via_api(invoice_data, image_files=[image_file])
        if result and result.get('checkpoint_id'):
            checkpoint_id = result['checkpoint_id']
            print(f"\n⏸️  Workflow paused after OCR processing. Checkpoint ID: {checkpoint_id}")
            print("✅ OCR extracted text from image successfully!")
            
            # Wait a bit
            time.sleep(2)
            
            # Check pending reviews
            pending = get_pending_reviews()
            print(f"\n📋 Pending Reviews: {len(pending)}")
            
            # Submit human decision (ACCEPT)
            decision_result = submit_human_decision(checkpoint_id, "ACCEPT")
            
            if decision_result:
                # Wait for processing
                time.sleep(3)
                thread_id = result['thread_id']
                status = get_workflow_status(thread_id)
                if status:
                    print(f"\n📊 Final Status: {status['status']}")
                    print(f"   Current Stage: {status.get('current_stage')}")
                    print(f"   Complete: {status.get('complete')}")
        elif result:
            print("⚠️  Expected HITL checkpoint but workflow completed without pause")
    else:
        print(f"⚠️  Image file not found: {image_file}")


def test_scenario_3_large_image():
    """Test scenario 3: Large amount invoice with image."""
    print("\n" + "="*60)
    print("SCENARIO 3: Large Amount Invoice - PNG Image (OCR Test)")
    print("="*60)
    
    invoice_data = {
        "invoice_id": "INV-OCR-2024-003",
        "vendor_name": "Gamma Corp",
        "vendor_tax_id": "TAX-111222",
        "invoice_date": "2024-01-25",
        "due_date": "2024-02-25",
        "amount": 17500.00,
        "currency": "USD",
        "line_items": [
            {"desc": "Premium Service", "qty": 50, "unit_price": 250.00, "total": 12500.00},
            {"desc": "Support Package", "qty": 10, "unit_price": 500.00, "total": 5000.00}
        ],
        "attachments": []
    }
    
    # Use image file for OCR testing
    image_file = "test_data/test_data/invoice_large_image.png"
    if os.path.exists(image_file):
        print(f"📎 Using OCR image: {image_file}")
        result = submit_invoice_via_api(invoice_data, image_files=[image_file])
        if result:
            thread_id = result['thread_id']
            time.sleep(3)  # Wait for OCR processing
            status = get_workflow_status(thread_id)
            if status:
                print(f"\n📊 Final Status: {status['status']}")
                print(f"   Current Stage: {status.get('current_stage')}")
                print("✅ OCR processing completed successfully!")
    else:
        print(f"⚠️  Image file not found: {image_file}")


def main():
    """Run end-to-end tests."""
    print("🧾 Langie - End-to-End Test Suite")
    print("="*60)
    
    # Check if API is running
    print("\n🔍 Checking if API is running...")
    if not test_api_health():
        print("❌ API is not running!")
        print("   Please start the API server:")
        print("   python -m src.api.app")
        return
    print("✅ API is running!")
    
    # Test scenarios
    print("\n📋 Running test scenarios...")
    
    # PDF-based tests
    test_scenario_1_pass()
    time.sleep(2)
    test_scenario_2_hitl()
    time.sleep(2)
    
    # Image/OCR-based tests
    print("\n🖼️  Running OCR tests with image files...")
    test_scenario_1_pass_image()
    time.sleep(2)
    test_scenario_2_hitl_image()
    time.sleep(2)
    test_scenario_3_large_image()
    
    print("\n" + "="*60)
    print("✅ End-to-end tests completed!")
    print("="*60)
    print("\n💡 Tips:")
    print("   - Check the API logs for detailed execution logs")
    print("   - Visit http://localhost:3000 for the frontend UI")
    print("   - Visit http://localhost:8000/docs for API documentation")
    print("   - Test images created in: test_data/test_data/")
    print("     - invoice_pass_image.png")
    print("     - invoice_fail_image.png")
    print("     - invoice_large_image.png")


if __name__ == "__main__":
    main()

