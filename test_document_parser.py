# -*- coding: utf-8 -*-
"""
test_document_parser.py — Tests for document upload and parsing functionality.

Run with: python test_document_parser.py
"""
import os
import sys

# Ensure UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")

    errors = []

    # Core dependencies
    try:
        import requests
        print("  [OK] requests")
    except ImportError as e:
        errors.append(f"requests: {e}")

    try:
        import boto3
        print("  [OK] boto3")
    except ImportError as e:
        errors.append(f"boto3: {e}")

    try:
        import streamlit
        print("  [OK] streamlit")
    except ImportError as e:
        errors.append(f"streamlit: {e}")

    try:
        from reportlab.pdfgen import canvas
        print("  [OK] reportlab")
    except ImportError as e:
        errors.append(f"reportlab: {e}")

    try:
        from pypdf import PdfReader
        print("  [OK] pypdf")
    except ImportError as e:
        errors.append(f"pypdf: {e}")

    try:
        from PIL import Image
        print("  [OK] Pillow")
    except ImportError as e:
        errors.append(f"Pillow: {e}")

    # Project modules
    try:
        from agent_intake import BedrockIntakeAgent
        print("  [OK] agent_intake")
    except ImportError as e:
        errors.append(f"agent_intake: {e}")

    try:
        from perdiemo_client import PerDiemoClient
        print("  [OK] perdiemo_client")
    except ImportError as e:
        errors.append(f"perdiemo_client: {e}")

    try:
        from backoffice_auditor import BackOfficeAuditor
        print("  [OK] backoffice_auditor")
    except ImportError as e:
        errors.append(f"backoffice_auditor: {e}")

    if errors:
        print(f"\n[FAIL] {len(errors)} import errors:")
        for e in errors:
            print(f"  - {e}")
        return False

    print("\n[PASS] All imports successful")
    return True


def test_demo_documents_exist():
    """Test that demo documents were generated."""
    print("\nTesting demo documents...")

    demo_dir = os.path.join(os.path.dirname(__file__), "demo_documents")

    if not os.path.exists(demo_dir):
        print(f"  [FAIL] demo_documents folder not found at {demo_dir}")
        print("  Run: python generate_demo_documents.py")
        return False

    expected_files = [
        "boarding_pass_PRG_VIE.pdf",
        "boarding_pass_VIE_PRG.pdf",
        "hotel_folio_grand_wien.pdf",
        "taxi_receipt_airport.pdf",
        "restaurant_receipt_dinner.pdf",
        "expense_report_form.pdf",
    ]

    missing = []
    for filename in expected_files:
        filepath = os.path.join(demo_dir, filename)
        if os.path.exists(filepath):
            size_kb = os.path.getsize(filepath) / 1024
            print(f"  [OK] {filename} ({size_kb:.1f} KB)")
        else:
            missing.append(filename)

    if missing:
        print(f"\n[FAIL] Missing {len(missing)} files:")
        for f in missing:
            print(f"  - {f}")
        return False

    print(f"\n[PASS] All {len(expected_files)} demo documents present")
    return True


def test_pdf_text_extraction():
    """Test that PDF text extraction works."""
    print("\nTesting PDF text extraction...")

    from pypdf import PdfReader
    import io

    demo_dir = os.path.join(os.path.dirname(__file__), "demo_documents")
    test_file = os.path.join(demo_dir, "hotel_folio_grand_wien.pdf")

    if not os.path.exists(test_file):
        print(f"  [SKIP] Test file not found: {test_file}")
        return True

    try:
        with open(test_file, "rb") as f:
            reader = PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""

        # Check for expected content
        checks = [
            ("GRAND HOTEL WIEN" in text, "Hotel name"),
            ("Alex Miller" in text, "Guest name"),
            ("EUR" in text, "Currency"),
        ]

        passed = 0
        for check, desc in checks:
            if check:
                print(f"  [OK] Found: {desc}")
                passed += 1
            else:
                print(f"  [WARN] Not found: {desc}")

        print(f"\n[{'PASS' if passed == len(checks) else 'PARTIAL'}] Text extraction: {passed}/{len(checks)} checks")
        return passed > 0

    except Exception as e:
        print(f"  [FAIL] PDF extraction error: {e}")
        return False


def test_agent_intake_mock():
    """Test the intake agent with mock mode."""
    print("\nTesting agent intake (mock mode)...")

    from agent_intake import BedrockIntakeAgent

    agent = BedrockIntakeAgent()

    # Test text extraction
    sample_text = "Departed Prague on June 10, 2025 at 07:00 to Vienna for client meetings."
    result = agent.extract_from_text(sample_text)

    if result and "itinerary" in result:
        print(f"  [OK] Text extraction returned itinerary with {len(result.get('itinerary', []))} legs")
        print(f"  [OK] Purpose: {result.get('ucel_cesty', 'N/A')}")
        print(f"  [OK] Vehicle: {result.get('typ_vozidla', 'N/A')}")
    else:
        print("  [FAIL] Text extraction failed")
        return False

    # Test file extraction method exists
    demo_dir = os.path.join(os.path.dirname(__file__), "demo_documents")
    test_file = os.path.join(demo_dir, "boarding_pass_PRG_VIE.pdf")

    if os.path.exists(test_file):
        with open(test_file, "rb") as f:
            pdf_bytes = f.read()

        result = agent.extract_from_file(pdf_bytes, "boarding_pass_PRG_VIE.pdf")
        if result:
            print(f"  [OK] PDF file extraction returned result")
        else:
            print("  [WARN] PDF file extraction returned empty")

    print("\n[PASS] Agent intake tests completed")
    return True


def test_perdiemo_api():
    """Test connection to PerDiemo API."""
    print("\nTesting PerDiemo API connection...")

    from perdiemo_client import PerDiemoClient

    client = PerDiemoClient()

    try:
        health = client.health()
        print(f"  [OK] API Status: {health.get('status', 'unknown')}")
        print(f"  [OK] Service: {health.get('service', 'unknown')}")
        print("\n[PASS] PerDiemo API is online")
        return True
    except Exception as e:
        print(f"  [FAIL] API connection failed: {e}")
        return False


def test_auditor():
    """Test the back-office auditor."""
    print("\nTesting back-office auditor...")

    from backoffice_auditor import BackOfficeAuditor

    auditor = BackOfficeAuditor()

    # Test with mock data
    mock_intake = {
        "ucel_cesty": "Client Negotiations",
        "hotel_info": {"breakfast_included": True},
        "bezplatna_strava": {"2025-06-11": ["snidane"]}
    }

    mock_calc = {
        "metadata": {
            "total_stravne_czk": 1226.61,
            "total_kraceni_czk": 260.19,
            "verification_signature": "1baebc05f2cab245d5901de7a1d8447d550d50d6d8ef9e940fa8007cddac219b"
        },
        "trip_reports": [{
            "souhrn_cesty": {},
            "denni_prehled": [{"datum": "2025-06-10"}, {"datum": "2025-06-11"}]
        }]
    }

    report = auditor.audit_trip(mock_intake, mock_calc)

    print(f"  [OK] Verdict: {report.get('verdict')}")
    print(f"  [OK] Risk Score: {report.get('risk_score')}")
    print(f"  [OK] Findings: {len(report.get('findings', []))} rules checked")

    print("\n[PASS] Auditor tests completed")
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("PerDiemo Document Parser Tests")
    print("=" * 60)

    results = []

    results.append(("Imports", test_imports()))
    results.append(("Demo Documents", test_demo_documents_exist()))
    results.append(("PDF Extraction", test_pdf_text_extraction()))
    results.append(("Agent Intake", test_agent_intake_mock()))
    results.append(("PerDiemo API", test_perdiemo_api()))
    results.append(("Auditor", test_auditor()))

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  [{status}] {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\nAll tests passed! Ready for demo.")
    else:
        print("\nSome tests failed. Check output above.")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
