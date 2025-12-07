# Auto-Complete Test Cases (No HITL Needed)

This document describes test cases for invoices that should **auto-complete** without triggering the Human-In-The-Loop (HITL) checkpoint.

## Conditions for Auto-Complete

For an invoice to auto-complete, it must satisfy:

1. **Match Score >= 0.90** (default threshold)
2. **Amount within tolerance**: `amount_diff_pct <= 5%` (default tolerance)
3. **Line items match**: All invoice line items match PO line items by description

### Match Score Calculation

```
match_score = (amount_score * 0.5) + (line_score * 0.5)

where:
- amount_score = 1.0 if amount_diff_pct <= tolerance_pct, else 0.0
- line_score = matched_line_items / total_line_items
```

## Test Cases

### 1. INV-AUTO-001: Perfect Match
**Description:** Exact amount and line items match PO-2024-001
- Amount: $1000.00 (exact match)
- Line Items: Widget A (10 × $50) + Widget B (5 × $100)
- **Expected:** Match score = 1.0, Auto-complete ✅

### 2. INV-AUTO-002: Within Tolerance (Small Increase)
**Description:** $5 difference (0.5%) within 5% tolerance
- Amount: $1005.00 (0.5% above PO)
- Line Items: Widget A (10 × $50) + Widget B (5 × $101)
- **Expected:** Match score >= 0.90, Auto-complete ✅

### 3. INV-AUTO-003: Within Tolerance (Small Decrease)
**Description:** $5 difference (0.5%) below original amount
- Amount: $995.00 (0.5% below PO)
- Line Items: Widget A (10 × $49.50) + Widget B (5 × $100)
- **Expected:** Match score >= 0.90, Auto-complete ✅

### 4. INV-AUTO-004: Within Tolerance (Medium Increase)
**Description:** $25 difference (2.5%) within 5% tolerance
- Amount: $1025.00 (2.5% above PO)
- Line Items: Widget A (10 × $50) + Widget B (5 × $105)
- **Expected:** Match score >= 0.90, Auto-complete ✅

### 5. INV-AUTO-005: Within Tolerance (Medium Decrease)
**Description:** $25 difference (2.5%) below original, still within 5%
- Amount: $975.00 (2.5% below PO)
- Line Items: Widget A (10 × $47.50) + Widget B (5 × $100)
- **Expected:** Match score >= 0.90, Auto-complete ✅

### 6. INV-AUTO-006: At Tolerance Boundary (Upper)
**Description:** $50 difference (5.0%) exactly at 5% tolerance
- Amount: $1050.00 (5.0% above PO)
- Line Items: Widget A (10 × $50) + Widget B (5 × $110)
- **Expected:** Match score >= 0.90, Auto-complete ✅

### 7. INV-AUTO-007: At Tolerance Boundary (Lower)
**Description:** $50 difference (5.0%) exactly at 5% tolerance (below)
- Amount: $950.00 (5.0% below PO)
- Line Items: Widget A (10 × $45) + Widget B (5 × $100)
- **Expected:** Match score >= 0.90, Auto-complete ✅

### 8. INV-AUTO-008: Description Variation
**Description:** Line item descriptions differ slightly but amounts match
- Amount: $1000.00 (exact match)
- Line Items: "Widget A - Premium" (10 × $50) + "Widget B - Standard" (5 × $100)
- **Expected:** Match score >= 0.90 (fuzzy description match), Auto-complete ✅

### 9. INV-AUTO-009: Vendor Name Normalization
**Description:** Vendor name normalization - "Acme Corporation" → "Acme Corp"
- Amount: $1000.00 (exact match)
- Vendor: "Acme Corporation" (normalizes to "Acme Corp")
- Line Items: Widget A (10 × $50) + Widget B (5 × $100)
- **Expected:** Match score = 1.0, Auto-complete ✅

### 10. INV-AUTO-010: Quantity/Price Variation (Same Total)
**Description:** Different quantity/price but same total
- Amount: $1000.00 (exact match)
- Line Items: Widget A (11 × $45.45 = $500) + Widget B (5 × $100)
- **Expected:** Match score >= 0.90, Auto-complete ✅

### 11. INV-AUTO-011: Quantity/Price Variation (Different Ratio)
**Description:** Different quantity/price ratio, same total
- Amount: $1000.00 (exact match)
- Line Items: Widget A (10 × $50) + Widget B (6 × $83.33 = $500)
- **Expected:** Match score >= 0.90, Auto-complete ✅

### 12. INV-AUTO-012: With PDF Attachment
**Description:** Perfect match with PDF attachment
- Amount: $1000.00 (exact match)
- Line Items: Widget A (10 × $50) + Widget B (5 × $100)
- Attachments: invoice_001.pdf
- **Expected:** OCR processes PDF, match score = 1.0, Auto-complete ✅

### 13. INV-AUTO-013: Single Line Item Match
**Description:** Partial PO match - only Widget A from PO-2024-001
- Amount: $500.00
- Line Items: Widget A (10 × $50)
- **Expected:** Match score >= 0.90 (one line item matches), Auto-complete ✅

### 14. INV-AUTO-014: Bulk Quantity Discount
**Description:** Bulk quantity discount - 20 units at $25 = same total as 10 at $50
- Amount: $1000.00 (exact match)
- Line Items: Widget A (20 × $25 = $500) + Widget B (5 × $100)
- **Expected:** Match score >= 0.90, Auto-complete ✅

### 15. INV-AUTO-015: Repeated Invoice
**Description:** Same invoice ID processed again should match same PO
- Amount: $1000.00 (exact match)
- Line Items: Widget A (10 × $50) + Widget B (5 × $100)
- **Expected:** Match score = 1.0, Auto-complete ✅

## Running the Tests

### Manual Testing via Frontend

1. Start the demo environment:
   ```bash
   ./demo.sh
   ```

2. Open frontend: http://localhost:5173

3. For each test case:
   - Go to "Submit Invoice" tab
   - Copy the JSON from `test_data/invoices_auto_complete.json`
   - Paste into the form
   - Submit
   - Verify workflow completes without appearing in "Human Review"

### Automated Testing

Run the automated test script:

```bash
# Make sure backend is running
python3 -m uvicorn src.api.app:app --host 0.0.0.0 --port 8000

# In another terminal, run tests
python3 test_auto_complete_scenarios.py
```

## Expected Results

All test cases should:
- ✅ Complete automatically (status = "COMPLETED")
- ✅ **NOT** appear in Human Review queue
- ✅ **NOT** trigger CHECKPOINT_HITL stage
- ✅ Have match_score >= 0.90
- ✅ Process through all 12 stages without pause

## Verification Checklist

After submitting each test case, verify:

- [ ] Workflow status is "COMPLETED"
- [ ] Workflow is NOT paused
- [ ] Invoice does NOT appear in Human Review queue
- [ ] Database Preview shows status = "COMPLETED"
- [ ] Database Preview shows decision = None (no HITL decision)
- [ ] All stages executed (intake through complete)
- [ ] Match score >= 0.90 in MATCH_TWO_WAY stage output

## Notes

- **Tolerance**: Default tolerance is 5%. Amounts within ±5% should auto-complete.
- **Line Item Matching**: Uses fuzzy description matching (substring match in demo).
- **Match Threshold**: Default threshold is 0.90. Any score >= 0.90 will auto-complete.
- **Amount Calculation**: Match score considers both amount difference and line item matches equally (50/50).

## Edge Cases

### What Triggers HITL?

These scenarios **will trigger HITL** (not in this test suite):

- Amount difference > 5% tolerance
- No matching PO found
- Line items don't match PO
- Match score < 0.90

See `test_data/invoice_fail.json` for examples of HITL-triggering scenarios.

