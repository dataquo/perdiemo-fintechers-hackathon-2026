# Demo Documents

Synthetic travel expense documents for hackathon demonstration.

## Documents

| File | Type | Key Data Points |
|------|------|-----------------|
| `boarding_pass_PRG_VIE.pdf` | Flight | Prague → Vienna, 10 Jun 2025, 07:00 |
| `boarding_pass_VIE_PRG.pdf` | Flight | Vienna → Prague, 11 Jun 2025, 18:30 |
| `hotel_folio_grand_wien.pdf` | Hotel | Grand Hotel Wien, **breakfast included**, EUR 190.92 |
| `taxi_receipt_airport.pdf` | Transport | Airport → Hotel, EUR 40.85 |
| `restaurant_receipt_dinner.pdf` | Meal | Business dinner, EUR 126.50 |
| `breakfast_receipt_fraud.pdf` | **FRAUD** | Breakfast receipt for same day hotel includes breakfast |
| `hotel_weekend_suspicious.pdf` | **ANOMALY** | Weekend spa trip without business justification |

## Demo Scenarios

### Scenario 1: Clean Trip (APPROVED)

Upload only `hotel_folio_grand_wien.pdf`:
- AI extracts breakfast included, declares it properly
- **Result:** APPROVED (Risk 0/100)

### Scenario 2: Fraud Detection (FLAGGED)

Upload both:
- `hotel_folio_grand_wien.pdf`
- `breakfast_receipt_fraud.pdf`

The hotel folio shows complimentary breakfast, but the employee also submits a separate breakfast receipt trying to get reimbursed twice.

**Result:** FLAGGED FOR REVIEW (Risk 45/100)
**Rule:** KB-RULE-01-MEAL-DOUBLE-DIPPING

### Scenario 3: Weekend Anomaly (WARNING)

Upload `hotel_weekend_suspicious.pdf`:
- Saturday-Sunday stay at spa resort
- No business justification
- Expensive spa treatments + champagne

**Result:** WARNING (KB-RULE-02-WEEKEND-TRAVEL-ANOMALY)

## How These Were Created

Generated using Python `reportlab` library:

```bash
python generate_fraud_document.py
```
