# -*- coding: utf-8 -*-
"""
generate_demo_documents.py — Creates synthetic demo documents for hackathon presentation.

Run this script to generate sample boarding passes, hotel folios, and receipts
in the demo_documents/ folder.

Usage:
    python generate_demo_documents.py
"""
import os
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "demo_documents")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def create_boarding_pass():
    """Create a synthetic boarding pass PDF."""
    filepath = os.path.join(OUTPUT_DIR, "boarding_pass_PRG_VIE.pdf")
    c = canvas.Canvas(filepath, pagesize=(210*mm, 100*mm))

    # Header
    c.setFillColor(HexColor('#004d99'))
    c.setFont("Helvetica-Bold", 18)
    c.drawString(10*mm, 85*mm, "BOARDING PASS")
    c.setFillColor(HexColor('#333333'))
    c.setFont("Helvetica", 12)
    c.drawString(140*mm, 85*mm, "Czech Airlines")

    # Passenger info
    c.setFont("Helvetica-Bold", 11)
    c.drawString(10*mm, 72*mm, "PASSENGER: MILLER / ALEX")
    c.setFont("Helvetica", 10)
    c.drawString(10*mm, 65*mm, "FLIGHT: OK 456")
    c.drawString(10*mm, 58*mm, "DATE: 10 JUN 2025")

    # From/To
    c.setFillColor(HexColor('#666666'))
    c.setFont("Helvetica", 8)
    c.drawString(10*mm, 48*mm, "FROM")
    c.drawString(70*mm, 48*mm, "TO")

    c.setFillColor(HexColor('#000000'))
    c.setFont("Helvetica-Bold", 14)
    c.drawString(10*mm, 40*mm, "PRAGUE (PRG)")
    c.drawString(70*mm, 40*mm, "VIENNA (VIE)")

    c.setFont("Helvetica", 10)
    c.drawString(10*mm, 33*mm, "Departure: 07:00")
    c.drawString(70*mm, 33*mm, "Arrival: 08:05")

    # Seat & Gate
    c.setFillColor(HexColor('#666666'))
    c.setFont("Helvetica", 8)
    c.drawString(150*mm, 65*mm, "SEAT")
    c.drawString(175*mm, 65*mm, "GATE")

    c.setFillColor(HexColor('#000000'))
    c.setFont("Helvetica-Bold", 18)
    c.drawString(150*mm, 52*mm, "12A")
    c.drawString(175*mm, 52*mm, "B7")

    c.setFont("Helvetica", 10)
    c.drawString(140*mm, 40*mm, "CLASS: BUSINESS")

    # Barcode placeholder
    c.rect(130*mm, 8*mm, 70*mm, 25*mm)
    c.setFont("Courier", 16)
    c.drawString(140*mm, 18*mm, "|||||||||||||||||||")

    c.save()
    print(f"Created: {filepath}")
    return filepath


def create_return_boarding_pass():
    """Create return flight boarding pass."""
    filepath = os.path.join(OUTPUT_DIR, "boarding_pass_VIE_PRG.pdf")
    c = canvas.Canvas(filepath, pagesize=(210*mm, 100*mm))

    c.setFillColor(HexColor('#004d99'))
    c.setFont("Helvetica-Bold", 18)
    c.drawString(10*mm, 85*mm, "BOARDING PASS")
    c.setFillColor(HexColor('#333333'))
    c.setFont("Helvetica", 12)
    c.drawString(140*mm, 85*mm, "Czech Airlines")

    c.setFont("Helvetica-Bold", 11)
    c.drawString(10*mm, 72*mm, "PASSENGER: MILLER / ALEX")
    c.setFont("Helvetica", 10)
    c.drawString(10*mm, 65*mm, "FLIGHT: OK 457")
    c.drawString(10*mm, 58*mm, "DATE: 11 JUN 2025")

    c.setFillColor(HexColor('#666666'))
    c.setFont("Helvetica", 8)
    c.drawString(10*mm, 48*mm, "FROM")
    c.drawString(70*mm, 48*mm, "TO")

    c.setFillColor(HexColor('#000000'))
    c.setFont("Helvetica-Bold", 14)
    c.drawString(10*mm, 40*mm, "VIENNA (VIE)")
    c.drawString(70*mm, 40*mm, "PRAGUE (PRG)")

    c.setFont("Helvetica", 10)
    c.drawString(10*mm, 33*mm, "Departure: 18:30")
    c.drawString(70*mm, 33*mm, "Arrival: 19:35")

    c.setFillColor(HexColor('#666666'))
    c.setFont("Helvetica", 8)
    c.drawString(150*mm, 65*mm, "SEAT")
    c.drawString(175*mm, 65*mm, "GATE")

    c.setFillColor(HexColor('#000000'))
    c.setFont("Helvetica-Bold", 18)
    c.drawString(150*mm, 52*mm, "14C")
    c.drawString(175*mm, 52*mm, "A3")

    c.setFont("Helvetica", 10)
    c.drawString(140*mm, 40*mm, "CLASS: BUSINESS")

    c.rect(130*mm, 8*mm, 70*mm, 25*mm)
    c.setFont("Courier", 16)
    c.drawString(140*mm, 18*mm, "|||||||||||||||||||")

    c.save()
    print(f"Created: {filepath}")
    return filepath


def create_hotel_folio():
    """Create a synthetic hotel invoice/folio PDF."""
    filepath = os.path.join(OUTPUT_DIR, "hotel_folio_grand_wien.pdf")
    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4

    # Hotel header
    c.setFillColor(HexColor('#1a1a4d'))
    c.setFont("Helvetica-Bold", 24)
    c.drawString(50, height - 50, "GRAND HOTEL WIEN")
    c.setFillColor(HexColor('#666666'))
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 70, "Kaerntner Ring 9, 1010 Vienna, Austria")
    c.drawString(50, height - 85, "Tel: +43 1 515 80 0 | www.grandhotelwien.com")

    # Invoice title
    c.setFillColor(HexColor('#000000'))
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 120, "GUEST FOLIO / INVOICE")
    c.line(50, height - 130, width - 50, height - 130)

    # Guest details
    y = height - 160
    c.setFillColor(HexColor('#666666'))
    c.setFont("Helvetica", 10)
    c.drawString(50, y, "Guest Name:")
    c.drawString(50, y - 20, "Company:")
    c.drawString(350, y, "Folio No:")
    c.drawString(350, y - 20, "Room:")

    c.setFillColor(HexColor('#000000'))
    c.setFont("Helvetica", 11)
    c.drawString(130, y, "Mr. Alex Miller")
    c.drawString(130, y - 20, "Komercni banka a.s.")
    c.drawString(420, y, "INV-2025-78456")
    c.drawString(420, y - 20, "Suite 412")

    # Stay details
    y -= 50
    c.setFillColor(HexColor('#666666'))
    c.setFont("Helvetica", 10)
    c.drawString(50, y, "Check-in:")
    c.drawString(350, y, "Check-out:")

    c.setFillColor(HexColor('#000000'))
    c.setFont("Helvetica", 11)
    c.drawString(130, y, "10 June 2025, 14:00")
    c.drawString(420, y, "11 June 2025, 11:00")

    # Table header
    y -= 50
    c.setFillColor(HexColor('#f0f0f0'))
    c.rect(50, y - 5, width - 100, 20, fill=True, stroke=False)
    c.setFillColor(HexColor('#000000'))
    c.setFont("Helvetica-Bold", 10)
    c.drawString(55, y, "Description")
    c.drawString(350, y, "Qty")
    c.drawString(400, y, "Rate")
    c.drawString(480, y, "Amount")

    # Line items
    items = [
        ("Business Suite - Corporate Rate", "1", "EUR 185.00", "EUR 185.00"),
        ("Complimentary Breakfast Buffet", "1", "Included", "EUR 0.00"),
        ("WiFi Premium", "1", "Included", "EUR 0.00"),
        ("City Tax (3.2%)", "1", "EUR 5.92", "EUR 5.92"),
    ]

    c.setFont("Helvetica", 10)
    y -= 25
    for desc, qty, rate, amount in items:
        c.drawString(55, y, desc)
        c.drawString(355, y, qty)
        c.drawString(400, y, rate)
        c.drawString(480, y, amount)
        y -= 20

    # Separator & total
    y -= 10
    c.line(50, y, width - 50, y)
    y -= 25
    c.setFont("Helvetica-Bold", 12)
    c.drawString(400, y, "TOTAL:")
    c.drawString(480, y, "EUR 190.92")

    # Payment
    y -= 40
    c.setFillColor(HexColor('#666666'))
    c.setFont("Helvetica", 10)
    c.drawString(50, y, "Payment Method:")
    c.setFillColor(HexColor('#000000'))
    c.drawString(150, y, "Corporate Mastercard ending 4892")

    # Note box
    y -= 40
    c.setFillColor(HexColor('#e6f2e6'))
    c.rect(50, y - 30, width - 100, 50, fill=True, stroke=False)
    c.setFillColor(HexColor('#2d7a2d'))
    c.setFont("Helvetica", 10)
    c.drawString(60, y + 5, "Note: Complimentary breakfast buffet included in corporate room rate.")
    c.setFillColor(HexColor('#333333'))
    c.setFont("Helvetica", 9)
    c.drawString(60, y - 10, "Breakfast served daily 06:30 - 10:30 in Restaurant Unkai.")

    # Footer
    c.setFillColor(HexColor('#666666'))
    c.setFont("Helvetica", 11)
    c.drawString(200, 50, "Thank you for staying with us!")

    c.save()
    print(f"Created: {filepath}")
    return filepath


def create_taxi_receipt():
    """Create a taxi receipt PDF."""
    filepath = os.path.join(OUTPUT_DIR, "taxi_receipt_airport.pdf")
    c = canvas.Canvas(filepath, pagesize=(105*mm, 148*mm))  # A6

    c.setFont("Helvetica-Bold", 14)
    c.drawString(10*mm, 138*mm, "TAXI VIENNA")
    c.setFillColor(HexColor('#666666'))
    c.setFont("Helvetica", 8)
    c.drawString(10*mm, 132*mm, "Lic. No: AT-VIE-4521")

    c.setFillColor(HexColor('#000000'))
    c.line(10*mm, 128*mm, 95*mm, 128*mm)

    c.setFont("Helvetica-Bold", 11)
    c.drawString(10*mm, 120*mm, "RECEIPT")
    c.setFont("Helvetica", 10)
    c.drawString(10*mm, 112*mm, "Date: 10.06.2025")
    c.drawString(10*mm, 105*mm, "Time: 11:15")

    c.drawString(10*mm, 92*mm, "From: Vienna Airport (VIE)")
    c.drawString(10*mm, 85*mm, "To: Grand Hotel Wien")

    c.drawString(10*mm, 72*mm, "Distance: 18.5 km")
    c.drawString(10*mm, 65*mm, "Duration: 25 min")

    c.line(10*mm, 58*mm, 95*mm, 58*mm)

    c.setFont("Helvetica", 9)
    c.drawString(10*mm, 50*mm, "Base fare:")
    c.drawString(70*mm, 50*mm, "EUR 3.80")
    c.drawString(10*mm, 43*mm, "Distance (18.5 km):")
    c.drawString(70*mm, 43*mm, "EUR 24.05")
    c.drawString(10*mm, 36*mm, "Airport surcharge:")
    c.drawString(70*mm, 36*mm, "EUR 13.00")

    c.line(10*mm, 30*mm, 95*mm, 30*mm)

    c.setFont("Helvetica-Bold", 11)
    c.drawString(10*mm, 22*mm, "TOTAL:")
    c.drawString(70*mm, 22*mm, "EUR 40.85")

    c.setFont("Helvetica", 8)
    c.drawString(10*mm, 12*mm, "Payment: Card ****4892")
    c.setFillColor(HexColor('#666666'))
    c.drawString(10*mm, 6*mm, "Driver: M. Hofer")

    c.save()
    print(f"Created: {filepath}")
    return filepath


def create_restaurant_receipt():
    """Create a restaurant/dinner receipt PDF."""
    filepath = os.path.join(OUTPUT_DIR, "restaurant_receipt_dinner.pdf")
    c = canvas.Canvas(filepath, pagesize=(105*mm, 170*mm))

    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(52.5*mm, 160*mm, "RESTAURANT OPUS")
    c.setFillColor(HexColor('#666666'))
    c.setFont("Helvetica", 9)
    c.drawCentredString(52.5*mm, 154*mm, "Imperial Hotel Vienna")
    c.drawCentredString(52.5*mm, 148*mm, "Kaerntner Ring 16, Wien")

    c.setFillColor(HexColor('#000000'))
    c.line(10*mm, 143*mm, 95*mm, 143*mm)

    c.setFont("Helvetica", 9)
    c.drawString(10*mm, 136*mm, "Date: 10.06.2025")
    c.drawString(55*mm, 136*mm, "Time: 19:45")
    c.drawString(10*mm, 129*mm, "Table: 12")
    c.drawString(55*mm, 129*mm, "Guests: 2")

    c.line(10*mm, 123*mm, 95*mm, 123*mm)

    items = [
        ("1x Wiener Schnitzel", "EUR 32.00"),
        ("1x Tafelspitz", "EUR 28.50"),
        ("2x House Salad", "EUR 14.00"),
        ("1x Apfelstrudel", "EUR 9.50"),
        ("2x Espresso", "EUR 7.00"),
        ("1x Gruner Veltliner 0.5l", "EUR 24.00"),
    ]

    y = 115*mm
    c.setFont("Helvetica", 9)
    for item, price in items:
        c.drawString(10*mm, y, item)
        c.drawString(75*mm, y, price)
        y -= 7*mm

    c.line(10*mm, y - 2*mm, 95*mm, y - 2*mm)

    y -= 10*mm
    c.drawString(10*mm, y, "Subtotal:")
    c.drawString(75*mm, y, "EUR 115.00")
    y -= 7*mm
    c.drawString(10*mm, y, "Service (10%):")
    c.drawString(75*mm, y, "EUR 11.50")

    c.line(10*mm, y - 5*mm, 95*mm, y - 5*mm)

    y -= 15*mm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(10*mm, y, "TOTAL:")
    c.drawString(70*mm, y, "EUR 126.50")

    y -= 15*mm
    c.setFont("Helvetica", 8)
    c.drawString(10*mm, y, "Payment: Corporate Card ****4892")

    c.setFillColor(HexColor('#666666'))
    c.setFont("Helvetica", 10)
    c.drawCentredString(52.5*mm, 10*mm, "Vielen Dank!")

    c.save()
    print(f"Created: {filepath}")
    return filepath


def create_expense_report_form():
    """Create a travel expense report form PDF."""
    filepath = os.path.join(OUTPUT_DIR, "expense_report_form.pdf")
    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4

    # Header
    c.setFillColor(HexColor('#003366'))
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 40, "KOMERCNI BANKA")
    c.setFont("Helvetica", 14)
    c.drawString(50, height - 60, "Travel Expense Report")
    c.setStrokeColor(HexColor('#003366'))
    c.setLineWidth(2)
    c.line(50, height - 70, width - 50, height - 70)

    # Employee info
    y = height - 100
    c.setFillColor(HexColor('#666666'))
    c.setFont("Helvetica", 10)
    c.drawString(50, y, "Employee:")
    c.drawString(300, y, "Employee ID:")
    c.drawString(50, y - 18, "Department:")
    c.drawString(300, y - 18, "Report Date:")

    c.setFillColor(HexColor('#000000'))
    c.setFont("Helvetica", 11)
    c.drawString(130, y, "Alex Miller")
    c.drawString(380, y, "KB-2024-1547")
    c.drawString(130, y - 18, "Corporate Banking")
    c.drawString(380, y - 18, "12 June 2025")

    # Trip details box
    y -= 55
    c.setFillColor(HexColor('#f0f0f0'))
    c.rect(50, y - 5, width - 100, 22, fill=True, stroke=False)
    c.setFillColor(HexColor('#000000'))
    c.setFont("Helvetica-Bold", 11)
    c.drawString(55, y, "TRIP DETAILS")

    y -= 30
    c.setFillColor(HexColor('#666666'))
    c.setFont("Helvetica", 10)
    c.drawString(50, y, "Purpose:")
    c.drawString(50, y - 18, "Destination:")
    c.drawString(300, y - 18, "Travel Dates:")

    c.setFillColor(HexColor('#000000'))
    c.setFont("Helvetica", 10)
    c.drawString(110, y, "Client Negotiations & Technology Demonstration - Vienna Branch")
    c.drawString(130, y - 18, "Vienna, Austria")
    c.drawString(380, y - 18, "10-11 June 2025")

    # Expense table header
    y -= 55
    c.setFillColor(HexColor('#d0d0e8'))
    c.rect(50, y - 5, width - 100, 22, fill=True, stroke=False)
    c.setFillColor(HexColor('#000000'))
    c.setFont("Helvetica-Bold", 9)
    c.drawString(55, y, "Date")
    c.drawString(100, y, "Category")
    c.drawString(180, y, "Description")
    c.drawString(400, y, "Currency")
    c.drawString(470, y, "Amount")

    # Expense items
    expenses = [
        ("10.06", "Transport", "Flight PRG-VIE (OK 456)", "CZK", "4,250.00"),
        ("10.06", "Transport", "Taxi Airport-Hotel", "EUR", "40.85"),
        ("10.06", "Lodging", "Grand Hotel Wien (1 night)", "EUR", "190.92"),
        ("10.06", "Meals", "Dinner - Restaurant Opus", "EUR", "126.50"),
        ("11.06", "Transport", "Flight VIE-PRG (OK 457)", "CZK", "4,250.00"),
    ]

    c.setFont("Helvetica", 9)
    y -= 22
    for date, cat, desc, curr, amt in expenses:
        c.drawString(55, y, date)
        c.drawString(100, y, cat)
        c.drawString(180, y, desc)
        c.drawString(408, y, curr)
        c.drawString(465, y, amt)
        y -= 18

    # Totals
    y -= 10
    c.setLineWidth(1)
    c.line(50, y, width - 50, y)
    y -= 20
    c.setFont("Helvetica", 10)
    c.drawString(350, y, "Total CZK:")
    c.drawString(450, y, "CZK 8,500.00")
    y -= 18
    c.drawString(350, y, "Total EUR:")
    c.drawString(450, y, "EUR 358.27")
    y -= 15
    c.line(350, y, width - 50, y)
    y -= 18
    c.setFont("Helvetica-Bold", 11)
    c.drawString(350, y, "GRAND TOTAL (CZK):")
    c.drawString(450, y, "CZK 17,456.78")
    c.setFillColor(HexColor('#666666'))
    c.setFont("Helvetica", 8)
    c.drawString(350, y - 12, "(EUR @ CNB rate 25.02)")

    # Attachments checklist box
    y -= 50
    c.setFillColor(HexColor('#f8f8f8'))
    c.rect(50, y - 80, 200, 90, fill=True, stroke=True)
    c.setFillColor(HexColor('#000000'))
    c.setFont("Helvetica-Bold", 9)
    c.drawString(55, y - 5, "ATTACHMENTS CHECKLIST:")

    c.setFont("Helvetica", 9)
    attachments = [
        "[X] Boarding passes (2)",
        "[X] Hotel folio",
        "[X] Taxi receipt",
        "[X] Restaurant receipt",
        "[ ] Other receipts"
    ]
    ay = y - 20
    for att in attachments:
        c.drawString(60, ay, att)
        ay -= 13

    # Signatures
    y = 80
    c.setFillColor(HexColor('#666666'))
    c.setFont("Helvetica", 10)
    c.drawString(50, y, "Employee Signature:")
    c.line(160, y, 280, y)
    c.setFillColor(HexColor('#3333aa'))
    c.setFont("Helvetica-Oblique", 12)
    c.drawString(170, y + 8, "A. Miller")

    c.setFillColor(HexColor('#666666'))
    c.setFont("Helvetica", 10)
    c.drawString(320, y, "Manager Approval:")
    c.line(430, y, width - 50, y)

    c.setFillColor(HexColor('#000000'))
    c.setFont("Helvetica", 9)
    c.drawString(50, y - 25, "Date: 12.06.2025")

    c.save()
    print(f"Created: {filepath}")
    return filepath


def main():
    """Generate all demo documents."""
    print("=" * 50)
    print("Generating synthetic demo documents...")
    print("=" * 50)
    print(f"Output directory: {OUTPUT_DIR}\n")

    files = [
        create_boarding_pass(),
        create_return_boarding_pass(),
        create_hotel_folio(),
        create_taxi_receipt(),
        create_restaurant_receipt(),
        create_expense_report_form(),
    ]

    print("\n" + "=" * 50)
    print(f"Created {len(files)} demo documents in: demo_documents/")
    print("=" * 50)
    print("\nFiles for demo:")
    for f in files:
        print(f"  - {os.path.basename(f)}")

    return files


if __name__ == "__main__":
    main()
