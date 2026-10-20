# Demo Documents

Synthetic travel expense documents for hackathon demonstration.

## How These Were Created

Generated programmatically using Python `reportlab` library to create realistic-looking PDFs that mimic real corporate travel documents.

**Generator script:** `generate_demo_documents.py`

```bash
python generate_demo_documents.py
```

## Documents

| File | Type | Key Data Points |
|------|------|-----------------|
| `boarding_pass_PRG_VIE.pdf` | Flight | Prague → Vienna, 10 Jun 2025, 07:00 |
| `boarding_pass_VIE_PRG.pdf` | Flight | Vienna → Prague, 11 Jun 2025, 18:30 |
| `hotel_folio_grand_wien.pdf` | Hotel | Grand Hotel Wien, **breakfast included**, EUR 190.92 |
| `taxi_receipt_airport.pdf` | Transport | Airport → Hotel, EUR 40.85 |
| `restaurant_receipt_dinner.pdf` | Meal | Business dinner, EUR 126.50 |

## Demo Scenario

**Business Trip: Prague → Vienna (2 days)**

- Employee: Alex Miller
- Company: Komerční banka client
- Purpose: Client negotiations
- Hotel: Grand Hotel Wien (breakfast included in rate)

## Key Demo Point

The `hotel_folio_grand_wien.pdf` contains **"Complimentary Breakfast Buffet Included"**.

When processed:
- AI extracts `breakfast_included: true`
- If employee declares breakfast as free meal → **APPROVED**
- If employee hides this (fraud simulation) → **FLAGGED** for meal double-dipping

This demonstrates the KB compliance rule: **KB-RULE-01-MEAL-DOUBLE-DIPPING**

## Regenerating Documents

```bash
cd /path/to/perdiemo
python generate_demo_documents.py
```

Documents are deterministic - same content each time.
