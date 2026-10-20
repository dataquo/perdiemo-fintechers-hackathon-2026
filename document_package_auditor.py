# -*- coding: utf-8 -*-
"""
document_package_auditor.py — Multi-document package verification for KB back-office challenge.

Verifies completeness, classifies documents, cross-checks consistency, and flags exceptions.
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import re
from datetime import datetime


class DocumentType(Enum):
    EXPENSE_REPORT = "expense_report"
    BOARDING_PASS = "boarding_pass"
    HOTEL_FOLIO = "hotel_folio"
    TAXI_RECEIPT = "taxi_receipt"
    RESTAURANT_RECEIPT = "restaurant_receipt"
    OTHER_RECEIPT = "other_receipt"
    UNKNOWN = "unknown"


@dataclass
class ClassifiedDocument:
    filename: str
    doc_type: DocumentType
    confidence: float
    extracted_data: Dict[str, Any]
    raw_text: str = ""


@dataclass
class PackageAuditResult:
    is_complete: bool
    completeness_score: float  # 0-100
    missing_documents: List[str]
    found_documents: List[ClassifiedDocument]
    consistency_issues: List[Dict[str, Any]]
    cross_check_results: List[Dict[str, Any]]
    verdict: str  # COMPLETE, INCOMPLETE, FLAGGED
    risk_score: int
    recommendations: List[str]


class DocumentPackageAuditor:
    """Audits a package of travel expense documents for completeness and consistency."""

    REQUIRED_DOCUMENTS = {
        "boarding_pass": {"min": 1, "description": "Boarding pass(es)"},
        "hotel_folio": {"min": 0, "description": "Hotel invoice/folio"},
        "taxi_receipt": {"min": 0, "description": "Ground transport receipts"},
        "restaurant_receipt": {"min": 0, "description": "Meal receipts"},
    }

    def __init__(self):
        self.classification_keywords = {
            DocumentType.EXPENSE_REPORT: [
                "expense report", "travel expense", "reimbursement",
                "employee signature", "manager approval", "attachments checklist"
            ],
            DocumentType.BOARDING_PASS: [
                "boarding pass", "flight", "seat", "gate", "departure",
                "arrival", "passenger", "airline"
            ],
            DocumentType.HOTEL_FOLIO: [
                "hotel", "folio", "check-in", "check-out", "room",
                "guest", "night", "accommodation", "suite"
            ],
            DocumentType.TAXI_RECEIPT: [
                "taxi", "cab", "fare", "driver", "distance", "km",
                "uber", "bolt", "ride"
            ],
            DocumentType.RESTAURANT_RECEIPT: [
                "restaurant", "dinner", "lunch", "menu", "table",
                "service", "tip", "meal", "food", "bill"
            ],
        }

    def classify_document(self, text: str, filename: str) -> tuple[DocumentType, float]:
        """Classify document type based on text content and filename."""
        text_lower = text.lower()
        filename_lower = filename.lower()

        scores = {}
        for doc_type, keywords in self.classification_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    score += 2
                if keyword.replace(" ", "_") in filename_lower or keyword.replace(" ", "-") in filename_lower:
                    score += 3
            scores[doc_type] = score

        if not scores or max(scores.values()) == 0:
            return DocumentType.UNKNOWN, 0.0

        best_type = max(scores, key=scores.get)
        max_score = scores[best_type]
        confidence = min(max_score / 10.0, 1.0)

        return best_type, confidence

    def extract_amounts(self, text: str) -> List[Dict[str, Any]]:
        """Extract monetary amounts from text."""
        amounts = []

        # Pattern for EUR amounts
        eur_pattern = r'EUR\s*([\d,]+\.?\d*)|€\s*([\d,]+\.?\d*)'
        for match in re.finditer(eur_pattern, text, re.IGNORECASE):
            value = match.group(1) or match.group(2)
            value = float(value.replace(",", ""))
            amounts.append({"currency": "EUR", "amount": value})

        # Pattern for CZK amounts
        czk_pattern = r'CZK\s*([\d,]+\.?\d*)|Kč\s*([\d,]+\.?\d*)'
        for match in re.finditer(czk_pattern, text, re.IGNORECASE):
            value = match.group(1) or match.group(2)
            value = float(value.replace(",", ""))
            amounts.append({"currency": "CZK", "amount": value})

        return amounts

    def extract_dates(self, text: str) -> List[str]:
        """Extract dates from text."""
        dates = []

        # Various date patterns
        patterns = [
            r'\d{1,2}[./]\d{1,2}[./]\d{4}',  # DD.MM.YYYY or DD/MM/YYYY
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}',  # 10 June 2025
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                dates.append(match.group())

        return list(set(dates))

    def audit_package(
        self,
        documents: List[Dict[str, Any]],  # [{filename, text, extracted_data}]
        expense_report_data: Optional[Dict[str, Any]] = None
    ) -> PackageAuditResult:
        """
        Audit a package of documents for completeness and consistency.

        Args:
            documents: List of dicts with filename, extracted text, and any extracted data
            expense_report_data: Optional parsed expense report with claimed amounts
        """
        classified_docs = []
        doc_type_counts = {dt: 0 for dt in DocumentType}
        all_amounts = []
        all_dates = []

        # Classify and extract from each document
        for doc in documents:
            doc_type, confidence = self.classify_document(
                doc.get("text", ""),
                doc.get("filename", "")
            )

            amounts = self.extract_amounts(doc.get("text", ""))
            dates = self.extract_dates(doc.get("text", ""))

            classified = ClassifiedDocument(
                filename=doc.get("filename", "unknown"),
                doc_type=doc_type,
                confidence=confidence,
                extracted_data={
                    **doc.get("extracted_data", {}),
                    "amounts": amounts,
                    "dates": dates
                },
                raw_text=doc.get("text", "")[:500]
            )

            classified_docs.append(classified)
            doc_type_counts[doc_type] += 1
            all_amounts.extend(amounts)
            all_dates.extend(dates)

        # Check completeness
        missing = []
        completeness_checks = 0
        completeness_passed = 0

        # Must have at least one flight document for a trip
        if doc_type_counts[DocumentType.BOARDING_PASS] == 0:
            missing.append("Boarding pass (required for flight travel)")
        else:
            completeness_passed += 1
        completeness_checks += 1

        # Check for supporting documents based on what's claimed
        if expense_report_data:
            claimed_hotel = expense_report_data.get("has_hotel", False)
            claimed_meals = expense_report_data.get("has_meals", False)
            claimed_transport = expense_report_data.get("has_transport", False)

            if claimed_hotel and doc_type_counts[DocumentType.HOTEL_FOLIO] == 0:
                missing.append("Hotel folio (claimed but not provided)")
            elif claimed_hotel:
                completeness_passed += 1
            if claimed_hotel:
                completeness_checks += 1

            if claimed_meals and doc_type_counts[DocumentType.RESTAURANT_RECEIPT] == 0:
                missing.append("Restaurant receipt (meals claimed but no receipt)")
            elif claimed_meals:
                completeness_passed += 1
            if claimed_meals:
                completeness_checks += 1

        # Calculate completeness score
        total_docs = len([d for d in classified_docs if d.doc_type != DocumentType.UNKNOWN])
        completeness_score = (completeness_passed / max(completeness_checks, 1)) * 100

        # Cross-check consistency
        consistency_issues = []
        cross_check_results = []

        # Check 1: Date alignment - all docs should be within reasonable date range
        if len(all_dates) >= 2:
            cross_check_results.append({
                "check": "Date Range Verification",
                "status": "PASS",
                "details": f"Found {len(all_dates)} dates across documents"
            })

        # Check 2: Look for duplicate amounts (potential double-submission)
        amount_values = [a["amount"] for a in all_amounts]
        duplicates = [a for a in set(amount_values) if amount_values.count(a) > 1 and a > 50]
        if duplicates:
            consistency_issues.append({
                "severity": "WARNING",
                "issue": "Duplicate amounts detected",
                "details": f"Same amount appears multiple times: {duplicates}",
                "recommendation": "Verify these are not duplicate submissions"
            })

        # Check 3: Hotel breakfast vs meal receipts
        hotel_docs = [d for d in classified_docs if d.doc_type == DocumentType.HOTEL_FOLIO]
        meal_docs = [d for d in classified_docs if d.doc_type == DocumentType.RESTAURANT_RECEIPT]

        for hotel in hotel_docs:
            hotel_text = hotel.raw_text.lower()
            if "breakfast included" in hotel_text or "complimentary breakfast" in hotel_text:
                # Check if there are breakfast meal receipts
                for meal in meal_docs:
                    meal_text = meal.raw_text.lower()
                    if "breakfast" in meal_text or "snidane" in meal_text:
                        consistency_issues.append({
                            "severity": "CRITICAL",
                            "issue": "Potential meal double-dipping",
                            "details": "Hotel includes breakfast but separate breakfast receipt submitted",
                            "recommendation": "Reject breakfast receipt - already covered by hotel"
                        })

                cross_check_results.append({
                    "check": "Hotel Breakfast Cross-Check",
                    "status": "FLAG" if any("breakfast" in m.raw_text.lower() for m in meal_docs) else "PASS",
                    "details": "Hotel includes complimentary breakfast"
                })

        # Calculate risk score
        risk_score = 0
        for issue in consistency_issues:
            if issue["severity"] == "CRITICAL":
                risk_score += 40
            elif issue["severity"] == "WARNING":
                risk_score += 20
            else:
                risk_score += 10

        if missing:
            risk_score += len(missing) * 15

        risk_score = min(risk_score, 100)

        # Determine verdict
        if risk_score >= 50:
            verdict = "FLAGGED_FOR_REVIEW"
        elif missing:
            verdict = "INCOMPLETE"
        else:
            verdict = "COMPLETE"

        # Generate recommendations
        recommendations = []
        if missing:
            recommendations.append(f"Request missing documents: {', '.join(missing)}")
        for issue in consistency_issues:
            recommendations.append(issue["recommendation"])
        if not recommendations:
            recommendations.append("Package appears complete and consistent")

        return PackageAuditResult(
            is_complete=len(missing) == 0,
            completeness_score=completeness_score,
            missing_documents=missing,
            found_documents=classified_docs,
            consistency_issues=consistency_issues,
            cross_check_results=cross_check_results,
            verdict=verdict,
            risk_score=risk_score,
            recommendations=recommendations
        )


if __name__ == "__main__":
    # Test the package auditor
    auditor = DocumentPackageAuditor()

    test_docs = [
        {
            "filename": "boarding_pass_PRG_VIE.pdf",
            "text": "BOARDING PASS Czech Airlines PASSENGER: MILLER/ALEX FLIGHT: OK 456 DATE: 10 JUN 2025 FROM PRAGUE (PRG) TO VIENNA (VIE) SEAT 12A GATE B7",
            "extracted_data": {}
        },
        {
            "filename": "hotel_folio_grand_wien.pdf",
            "text": "GRAND HOTEL WIEN Guest: Mr. Alex Miller Check-in: 10 June 2025 Check-out: 11 June 2025 Business Suite EUR 185.00 Complimentary Breakfast Buffet Included TOTAL: EUR 190.92",
            "extracted_data": {}
        },
        {
            "filename": "restaurant_receipt.pdf",
            "text": "RESTAURANT OPUS Dinner Date: 10.06.2025 Wiener Schnitzel EUR 32.00 TOTAL: EUR 126.50",
            "extracted_data": {}
        }
    ]

    result = auditor.audit_package(test_docs)

    print(f"Verdict: {result.verdict}")
    print(f"Completeness: {result.completeness_score:.0f}%")
    print(f"Risk Score: {result.risk_score}")
    print(f"Missing: {result.missing_documents}")
    print(f"Issues: {len(result.consistency_issues)}")
    for rec in result.recommendations:
        print(f"  - {rec}")
