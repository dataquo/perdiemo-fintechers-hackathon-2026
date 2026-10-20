# -*- coding: utf-8 -*-
"""
generate_tsys_data.py — Generates realistic synthetic TSYS corporate credit card feeds.
Includes:
- Business travel expenses to Vienna (June 10-12, 2025)
- Company card transactions (rail, fuel, toll, hotel, uber, business dinner)
- Personal expense on company card (Billa grocery snack)
- Non-travel office expense (Alza electronics)
- Out-of-pocket cash expense (Local Vienna city taxi)
"""
import json
import csv
from pathlib import Path

TSYS_TRANSACTIONS = [
    {
        "transaction_id": "TSYS-KB-20250610-001",
        "card_token": "KB-CORP-VISA-4819",
        "cardholder_name": "Alex Miller",
        "employee_id": "EMP-KB-0042",
        "company_name": "Komerční banka Corporate Client a.s.",
        "timestamp": "2025-06-10T06:45:00",
        "merchant_descriptor": "CD E-SHOP PRAHA 1 CZ",
        "merchant_name": "České dráhy e-shop",
        "mcc": 4112,
        "mcc_category": "Passenger Railways",
        "amount": 890.00,
        "currency": "CZK",
        "billing_amount_czk": 890.00,
        "merchant_city": "Prague",
        "merchant_country": "CZE",
        "status": "SETTLED",
        "is_company_card": True,
        "expense_type": "TRAVEL_TRANSPORT",
        "notes": "Seat reservation & train ticket Prague -> Brno/Breclav"
    },
    {
        "transaction_id": "TSYS-KB-20250610-002",
        "card_token": "KB-CORP-VISA-4819",
        "cardholder_name": "Alex Miller",
        "employee_id": "EMP-KB-0042",
        "company_name": "Komerční banka Corporate Client a.s.",
        "timestamp": "2025-06-10T09:15:00",
        "merchant_descriptor": "SHELL 4102 MIKULOV CZ",
        "merchant_name": "Shell Mikulov",
        "mcc": 5541,
        "mcc_category": "Service Stations / Fuel",
        "amount": 1650.00,
        "currency": "CZK",
        "billing_amount_czk": 1650.00,
        "merchant_city": "Mikulov",
        "merchant_country": "CZE",
        "status": "SETTLED",
        "is_company_card": True,
        "expense_type": "TRAVEL_FUEL",
        "notes": "Company car refueling before Austrian border"
    },
    {
        "transaction_id": "TSYS-KB-20250610-003",
        "card_token": "KB-CORP-VISA-4819",
        "cardholder_name": "Alex Miller",
        "employee_id": "EMP-KB-0042",
        "company_name": "Komerční banka Corporate Client a.s.",
        "timestamp": "2025-06-10T09:45:00",
        "merchant_descriptor": "ASFINAG MAUTSTELLE A5 AUT",
        "merchant_name": "Asfinag Autobahnen Maut",
        "mcc": 4784,
        "mcc_category": "Tolls and Bridge Fees",
        "amount": 11.50,
        "currency": "EUR",
        "billing_amount_czk": 289.80,
        "merchant_city": "Schrick",
        "merchant_country": "AUT",
        "status": "SETTLED",
        "is_company_card": True,
        "expense_type": "TRAVEL_TOLL",
        "notes": "Austrian 10-day digital motorway vignette"
    },
    {
        "transaction_id": "TSYS-KB-20250610-004",
        "card_token": "KB-CORP-VISA-4819",
        "cardholder_name": "Alex Miller",
        "employee_id": "EMP-KB-0042",
        "company_name": "Komerční banka Corporate Client a.s.",
        "timestamp": "2025-06-10T12:30:00",
        "merchant_descriptor": "CAFE CENTRAL WIEN AUT",
        "merchant_name": "Café Central Wien",
        "mcc": 5812,
        "mcc_category": "Eating Places and Restaurants",
        "amount": 28.50,
        "currency": "EUR",
        "billing_amount_czk": 718.20,
        "merchant_city": "Vienna",
        "merchant_country": "AUT",
        "status": "SETTLED",
        "is_company_card": True,
        "expense_type": "TRAVEL_MEAL",
        "notes": "Client meeting lunch (Alex Miller + Dr. Gruber, Erste Group)"
    },
    {
        "transaction_id": "TSYS-KB-20250611-005",
        "card_token": "KB-CORP-VISA-4819",
        "cardholder_name": "Alex Miller",
        "employee_id": "EMP-KB-0042",
        "company_name": "Komerční banka Corporate Client a.s.",
        "timestamp": "2025-06-11T16:20:00",
        "merchant_descriptor": "UBER *TRIP VIENNA BV HELP.UBER.COM",
        "merchant_name": "Uber Vienna",
        "mcc": 4121,
        "mcc_category": "Taxicabs and Limousines",
        "amount": 18.40,
        "currency": "EUR",
        "billing_amount_czk": 463.68,
        "merchant_city": "Vienna",
        "merchant_country": "AUT",
        "status": "SETTLED",
        "is_company_card": True,
        "expense_type": "TRAVEL_TRANSPORT",
        "notes": "Transport from client office (Am Belvedere) to hotel"
    },
    {
        "transaction_id": "TSYS-KB-20250611-006",
        "card_token": "KB-CORP-VISA-4819",
        "cardholder_name": "Alex Miller",
        "employee_id": "EMP-KB-0042",
        "company_name": "Komerční banka Corporate Client a.s.",
        "timestamp": "2025-06-11T19:30:00",
        "merchant_descriptor": "RESTAURANT PLACHUTTA WIEN AUT",
        "merchant_name": "Plachutta Wollzeile",
        "mcc": 5812,
        "mcc_category": "Eating Places and Restaurants",
        "amount": 95.00,
        "currency": "EUR",
        "billing_amount_czk": 2394.00,
        "merchant_city": "Vienna",
        "merchant_country": "AUT",
        "status": "SETTLED",
        "is_company_card": True,
        "expense_type": "TRAVEL_MEAL",
        "notes": "Business dinner with Austrian client team"
    },
    {
        "transaction_id": "TSYS-KB-20250612-007",
        "card_token": "KB-CORP-VISA-4819",
        "cardholder_name": "Alex Miller",
        "employee_id": "EMP-KB-0042",
        "company_name": "Komerční banka Corporate Client a.s.",
        "timestamp": "2025-06-12T08:30:00",
        "merchant_descriptor": "GRAND HOTEL WIEN VIENNA AUT",
        "merchant_name": "Grand Hotel Wien",
        "mcc": 7011,
        "mcc_category": "Hotels and Motels",
        "amount": 340.00,
        "currency": "EUR",
        "billing_amount_czk": 8568.00,
        "merchant_city": "Vienna",
        "merchant_country": "AUT",
        "status": "SETTLED",
        "is_company_card": True,
        "expense_type": "TRAVEL_LODGING",
        "hotel_details": {
            "nights": 2,
            "check_in": "2025-06-10",
            "check_out": "2025-06-12",
            "breakfast_included": True,
            "breakfast_dates": ["2025-06-11", "2025-06-12"]
        },
        "notes": "2 nights accommodation (Classic King Room), complimentary breakfast included in rate"
    },
    {
        "transaction_id": "TSYS-KB-20250612-008",
        "card_token": "KB-CORP-VISA-4819",
        "cardholder_name": "Alex Miller",
        "employee_id": "EMP-KB-0042",
        "company_name": "Komerční banka Corporate Client a.s.",
        "timestamp": "2025-06-12T13:10:00",
        "merchant_descriptor": "BILLA FIL. 481 WIEN AUT",
        "merchant_name": "Billa Supermarket",
        "mcc": 5411,
        "mcc_category": "Grocery Stores and Supermarkets",
        "amount": 14.80,
        "currency": "EUR",
        "billing_amount_czk": 372.96,
        "merchant_city": "Vienna",
        "merchant_country": "AUT",
        "status": "SETTLED",
        "is_company_card": True,
        "expense_type": "PERSONAL_EXPENSE",
        "notes": "Personal snacks & beverages (flagged for salary deduction or offset)"
    },
    {
        "transaction_id": "TSYS-KB-20250614-009",
        "card_token": "KB-CORP-VISA-4819",
        "cardholder_name": "Alex Miller",
        "employee_id": "EMP-KB-0042",
        "company_name": "Komerční banka Corporate Client a.s.",
        "timestamp": "2025-06-14T11:00:00",
        "merchant_descriptor": "ALZA.CZ PRAHA 7 CZ",
        "merchant_name": "Alza.cz",
        "mcc": 5732,
        "mcc_category": "Electronic Sales",
        "amount": 1490.00,
        "currency": "CZK",
        "billing_amount_czk": 1490.00,
        "merchant_city": "Prague",
        "merchant_country": "CZE",
        "status": "SETTLED",
        "is_company_card": True,
        "expense_type": "OFFICE_SUPPLIES",
        "notes": "USB-C docking adapter for office (non-travel expense, excluded from trip per diem)"
    }
]

# Out of pocket cash expense (paid personally by Alex Miller, requiring reimbursement)
OUT_OF_POCKET_EXPENSES = [
    {
        "expense_id": "OOP-CASH-20250612-01",
        "claimant": "Alex Miller",
        "timestamp": "2025-06-12T14:45:00",
        "merchant_name": "Vienna City Taxi 40100 (Cash)",
        "amount": 25.00,
        "currency": "EUR",
        "payment_method": "PERSONAL_CASH",
        "notes": "Emergency taxi to train station when Uber was unavailable. Paper receipt attached."
    }
]

def main():
    out_dir = Path("sample_data")
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / "tsys_card_feed.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "account_id": "KB-CORP-ACC-99214",
            "corporate_client": "Komerční banka Corporate Client a.s.",
            "cardholder": "Alex Miller",
            "employee_id": "EMP-KB-0042",
            "employee_iban": "CZ6501000000001928374650",
            "transactions": TSYS_TRANSACTIONS,
            "out_of_pocket_cash": OUT_OF_POCKET_EXPENSES
        }, f, indent=2, ensure_ascii=False)
    print(f"Wrote {json_path} ({len(TSYS_TRANSACTIONS)} transactions)")

    csv_path = out_dir / "tsys_card_feed.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "transaction_id", "card_token", "cardholder_name", "timestamp",
            "merchant_descriptor", "merchant_name", "mcc", "mcc_category",
            "amount", "currency", "billing_amount_czk", "merchant_city",
            "merchant_country", "status", "expense_type", "notes"
        ])
        writer.writeheader()
        for tx in TSYS_TRANSACTIONS:
            row = {k: v for k, v in tx.items() if k in writer.fieldnames}
            writer.writerow(row)
    print(f"Wrote {csv_path}")

if __name__ == "__main__":
    main()
