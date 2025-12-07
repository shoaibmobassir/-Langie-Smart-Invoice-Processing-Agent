"""Create all test data including PDFs."""

import os
import json
import subprocess
import sys

def create_pdfs():
    """Create PDF files for testing."""
    print("Creating PDF files...")
    try:
        # Try to run the PDF creation script
        result = subprocess.run([sys.executable, "create_test_pdfs.py"], 
                              cwd="test_data", 
                              capture_output=True, 
                              text=True)
        print(result.stdout)
        if result.stderr:
            print("Warnings:", result.stderr)
        return True
    except Exception as e:
        print(f"Could not create PDFs: {e}")
        # Create simple text files instead
        print("Creating text file placeholders...")
        os.makedirs("test_data", exist_ok=True)
        
        invoices = {
            "invoice_001.pdf": """INVOICE
Invoice ID: INV-2024-001
Vendor: Acme Corporation
Tax ID: TAX-123456
Invoice Date: 2024-01-15
Due Date: 2024-02-15

Line Item 1: Widget A - Qty: 10, Price: $50.00, Total: $500.00
Line Item 2: Widget B - Qty: 5, Price: $100.00, Total: $500.00

PO Reference: PO-2024-001
Total: $1000.00""",
            
            "invoice_002.pdf": """INVOICE
Invoice ID: INV-2024-002
Vendor: Beta Industries
Tax ID: TAX-789012
Invoice Date: 2024-01-20
Due Date: 2024-02-20

Line Item 1: Unknown Item - Qty: 100, Price: $60.00, Total: $6000.00

Total: $6000.00""",
            
            "invoice_003.pdf": """INVOICE
Invoice ID: INV-2024-003
Vendor: Gamma Supplies Inc
Tax ID: TAX-345678
Invoice Date: 2024-01-25
Due Date: 2024-02-25

Line Item 1: Enterprise Software License - Qty: 1, Price: $15000.00, Total: $15000.00

Total: $15000.00""",
            
            "invoice_004.pdf": """INVOICE
Invoice ID: INV-2024-004
Vendor: Delta Services
Invoice Date: 2024-01-30

Line Item 1: Consulting Services - Qty: 50, Price: $50.00, Total: $2500.00

Total: $2500.00"""
        }
        
        for filename, content in invoices.items():
            with open(f"test_data/{filename}", "w") as f:
                f.write(content)
        
        print("✅ Text file placeholders created!")
        return True

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    create_pdfs()
    print("\n✅ All test data created!")

