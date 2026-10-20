# -*- coding: utf-8 -*-
"""
tests/test_invoice_matcher.py — Tests for 2-Way Invoice vs Banking Reconciliation.
"""
from invoice_matcher import InvoiceTransactionMatcher

def test_invoice_transaction_matcher_basic():
    matcher = InvoiceTransactionMatcher(cnb_rate=25.12)
    report = matcher.reconcile()

    assert report is not None
    assert "verdict" in report
    assert "risk_score" in report
    assert "metrics" in report
    assert "results" in report

    metrics = report["metrics"]
    assert metrics["exact_matches"] >= 2
    assert metrics["discrepancies"] >= 1
    assert metrics["out_of_pocket_invoices"] >= 1
    assert metrics["missing_invoices"] >= 1
    assert metrics["personal_offsets"] >= 1

    # Verify matching items
    statuses = [r["match_status"] for r in report["results"]]
    assert "EXACT_MATCH" in statuses
    assert "AMOUNT_DISCREPANCY" in statuses
    assert "ORPHAN_INVOICE" in statuses
    assert "ORPHAN_CARD_TRANSACTION" in statuses
    assert "PERSONAL_CHARGE_OFFSET" in statuses

def test_invoice_builder_from_extractions():
    matcher = InvoiceTransactionMatcher()
    sample_extractions = [
        {"filename": "hotel_folio_grand_wien.pdf", "data": {"document_type": "hotel_folio"}},
        {"filename": "restaurant_receipt_dinner.pdf", "data": {"document_type": "meal_receipt", "meal_receipt": {"amount": 126.50, "currency": "EUR"}}}
    ]
    invoices = matcher.build_invoices_from_extractions(sample_extractions)
    assert len(invoices) == 2
    assert invoices[0]["vendor_name"] == "Grand Hotel Wien"
    assert invoices[1]["amount"] == 126.50
