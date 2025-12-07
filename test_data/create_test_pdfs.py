"""Create test PDF files for OCR testing."""

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch
    import os
    
    def create_invoice_pdf(filename, invoice_data):
        """Create a PDF invoice for OCR testing."""
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter
        
        # Title
        c.setFont("Helvetica-Bold", 20)
        c.drawString(50, height - 50, "INVOICE")
        
        # Invoice details
        c.setFont("Helvetica", 12)
        y = height - 100
        c.drawString(50, y, f"Invoice ID: {invoice_data['invoice_id']}")
        y -= 20
        c.drawString(50, y, f"Vendor: {invoice_data['vendor_name']}")
        y -= 20
        c.drawString(50, y, f"Tax ID: {invoice_data.get('vendor_tax_id', 'N/A')}")
        y -= 20
        c.drawString(50, y, f"Invoice Date: {invoice_data['invoice_date']}")
        y -= 20
        c.drawString(50, y, f"Due Date: {invoice_data['due_date']}")
        
        # Line items header
        y -= 40
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Description")
        c.drawString(300, y, "Qty")
        c.drawString(350, y, "Unit Price")
        c.drawString(450, y, "Total")
        
        # Line items
        y -= 25
        c.setFont("Helvetica", 10)
        total = 0
        for item in invoice_data['line_items']:
            c.drawString(50, y, item['desc'])
            c.drawString(300, y, str(item['qty']))
            c.drawString(350, y, f"${item['unit_price']:.2f}")
            c.drawString(450, y, f"${item['total']:.2f}")
            total += item['total']
            y -= 20
        
        # Total
        y -= 20
        c.setFont("Helvetica-Bold", 12)
        c.drawString(350, y, "TOTAL:")
        c.drawString(450, y, f"${total:.2f}")
        
        # PO Reference
        y -= 40
        c.setFont("Helvetica", 10)
        c.drawString(50, y, "PO Reference: PO-2024-001")
        
        c.save()
        print(f"Created PDF: {filename}")
    
    # Create test data directory
    os.makedirs("test_data", exist_ok=True)
    
    # Create invoice 001 (will pass matching)
    invoice_001 = {
        "invoice_id": "INV-2024-001",
        "vendor_name": "Acme Corporation",
        "vendor_tax_id": "TAX-123456",
        "invoice_date": "2024-01-15",
        "due_date": "2024-02-15",
        "line_items": [
            {"desc": "Widget A", "qty": 10, "unit_price": 50.00, "total": 500.00},
            {"desc": "Widget B", "qty": 5, "unit_price": 100.00, "total": 500.00}
        ]
    }
    create_invoice_pdf("test_data/invoice_001.pdf", invoice_001)
    
    # Create invoice 002 (will fail matching)
    invoice_002 = {
        "invoice_id": "INV-2024-002",
        "vendor_name": "Beta Industries",
        "vendor_tax_id": "TAX-789012",
        "invoice_date": "2024-01-20",
        "due_date": "2024-02-20",
        "line_items": [
            {"desc": "Unknown Item", "qty": 100, "unit_price": 60.00, "total": 6000.00}
        ]
    }
    create_invoice_pdf("test_data/invoice_002.pdf", invoice_002)
    
    print("\n✅ Test PDFs created successfully!")
    
except ImportError:
    print("⚠️  reportlab not installed. Creating text-based mock PDFs...")
    import os
    # Create simple text files as PDF placeholders
    os.makedirs("test_data", exist_ok=True)
    
    with open("test_data/invoice_001.pdf", "w") as f:
        f.write("""INVOICE
Invoice ID: INV-2024-001
Vendor: Acme Corporation
Tax ID: TAX-123456
Invoice Date: 2024-01-15
Due Date: 2024-02-15

Line Items:
Widget A - Qty: 10, Price: $50.00, Total: $500.00
Widget B - Qty: 5, Price: $100.00, Total: $500.00

PO Reference: PO-2024-001
Total: $1000.00
""")
    
    with open("test_data/invoice_002.pdf", "w") as f:
        f.write("""INVOICE
Invoice ID: INV-2024-002
Vendor: Beta Industries
Tax ID: TAX-789012
Invoice Date: 2024-01-20
Due Date: 2024-02-20

Line Items:
Unknown Item - Qty: 100, Price: $60.00, Total: $6000.00

Total: $6000.00
""")
    
    print("✅ Mock PDF files created!")

