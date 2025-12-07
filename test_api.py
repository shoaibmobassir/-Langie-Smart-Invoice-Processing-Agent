"""Simple API test script."""

import requests
import json

API_BASE = "http://localhost:8000"

# Test invoice
invoice = {
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
    "attachments": ["test_data/invoice_001.pdf"]
}

print("Testing API endpoint...")
print(f"Sending: {json.dumps(invoice, indent=2)}")

response = requests.post(
    f"{API_BASE}/workflow/run",
    json=invoice,
    headers={"Content-Type": "application/json"}
)

print(f"\nStatus: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

