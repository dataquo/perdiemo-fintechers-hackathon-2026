"""Generate a fraudulent breakfast receipt that triggers KB-RULE-01 when uploaded with hotel folio."""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black, gray
import os

def create_breakfast_receipt():
    """Create a breakfast receipt for dates when hotel already included breakfast."""

    output_dir = "demo_documents"
    filepath = os.path.join(output_dir, "breakfast_receipt_fraud.pdf")

    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width/2, height - 30*mm, "Cafe Central Vienna")

    c.setFont("Helvetica", 10)
    c.drawCentredString(width/2, height - 38*mm, "Herrengasse 14, 1010 Wien, Austria")
    c.drawCentredString(width/2, height - 44*mm, "Tel: +43 1 533 37 63")

    # Receipt title
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width/2, height - 58*mm, "RECEIPT / RECHNUNG")

    # Receipt details
    c.setFont("Helvetica", 11)
    y = height - 75*mm

    c.drawString(30*mm, y, "Date: 11 June 2025")  # Same date as hotel checkout
    c.drawString(120*mm, y, "Receipt No: 2025-06-11-0847")

    y -= 15*mm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(30*mm, y, "Guest: Alex Miller")
    c.drawString(120*mm, y, "Table: 12")

    # Line
    y -= 8*mm
    c.setStrokeColor(gray)
    c.line(25*mm, y, 185*mm, y)

    # Items header
    y -= 10*mm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(30*mm, y, "Description")
    c.drawString(130*mm, y, "Qty")
    c.drawString(160*mm, y, "EUR")

    # Items - BREAKFAST items (this is the fraud - hotel already included breakfast)
    y -= 8*mm
    c.setFont("Helvetica", 10)

    items = [
        ("Wiener Fruhstuck (Full Breakfast)", "1", "18.50"),
        ("Fresh Orange Juice", "1", "5.90"),
        ("Cappuccino", "2", "9.80"),
        ("Croissant with Butter", "1", "4.50"),
    ]

    for desc, qty, price in items:
        c.drawString(30*mm, y, desc)
        c.drawString(135*mm, y, qty)
        c.drawString(160*mm, y, price)
        y -= 6*mm

    # Subtotal line
    y -= 5*mm
    c.line(25*mm, y, 185*mm, y)

    # Totals
    y -= 10*mm
    c.setFont("Helvetica", 10)
    c.drawString(120*mm, y, "Subtotal:")
    c.drawString(160*mm, y, "38.70")

    y -= 6*mm
    c.drawString(120*mm, y, "VAT (10%):")
    c.drawString(160*mm, y, "3.87")

    y -= 8*mm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(120*mm, y, "TOTAL:")
    c.drawString(160*mm, y, "EUR 42.57")

    # Payment method
    y -= 15*mm
    c.setFont("Helvetica", 10)
    c.drawString(30*mm, y, "Payment: Corporate Card ****4829")

    # Footer note - THIS IS KEY for AI extraction
    y -= 20*mm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(30*mm, y, "BUSINESS EXPENSE - BREAKFAST")
    c.setFont("Helvetica", 9)
    y -= 6*mm
    c.drawString(30*mm, y, "Purpose: Client meeting preparation breakfast")

    # Thank you
    y -= 20*mm
    c.setFont("Helvetica-Oblique", 10)
    c.drawCentredString(width/2, y, "Vielen Dank fur Ihren Besuch!")
    c.drawCentredString(width/2, y - 5*mm, "Thank you for your visit!")

    c.save()
    print(f"Created: {filepath}")
    return filepath


def create_weekend_trip_docs():
    """Create documents for a weekend trip without business justification (KB-RULE-02)."""

    output_dir = "demo_documents"
    filepath = os.path.join(output_dir, "hotel_weekend_suspicious.pdf")

    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4

    # Hotel header
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width/2, height - 25*mm, "HOTEL & SPA KARLOVY VARY")

    c.setFont("Helvetica", 10)
    c.drawCentredString(width/2, height - 33*mm, "Trziste 9, 360 01 Karlovy Vary, Czech Republic")

    # Folio title
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width/2, height - 48*mm, "GUEST FOLIO")

    # Guest info
    y = height - 65*mm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(30*mm, y, "Guest Name:")
    c.setFont("Helvetica", 11)
    c.drawString(70*mm, y, "Alex Miller")

    y -= 8*mm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(30*mm, y, "Company:")
    c.setFont("Helvetica", 11)
    c.drawString(70*mm, y, "KB Enterprise Client")

    # WEEKEND DATES - Saturday to Sunday (suspicious)
    y -= 8*mm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(30*mm, y, "Check-in:")
    c.setFont("Helvetica", 11)
    c.drawString(70*mm, y, "Saturday, 14 June 2025, 15:00")

    y -= 8*mm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(30*mm, y, "Check-out:")
    c.setFont("Helvetica", 11)
    c.drawString(70*mm, y, "Sunday, 15 June 2025, 11:00")

    y -= 8*mm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(30*mm, y, "Room:")
    c.setFont("Helvetica", 11)
    c.drawString(70*mm, y, "Deluxe Spa Suite #301")

    # Line
    y -= 12*mm
    c.line(25*mm, y, 185*mm, y)

    # Charges
    y -= 10*mm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(30*mm, y, "Description")
    c.drawString(150*mm, y, "Amount")

    y -= 8*mm
    c.setFont("Helvetica", 10)

    charges = [
        ("Deluxe Spa Suite (1 night)", "CZK 4,500"),
        ("Spa Treatment - Full Body Massage", "CZK 2,200"),
        ("Spa Treatment - Thermal Bath Package", "CZK 1,500"),
        ("Minibar", "CZK 890"),
        ("Room Service - Champagne", "CZK 1,200"),
    ]

    for desc, amount in charges:
        c.drawString(30*mm, y, desc)
        c.drawString(150*mm, y, amount)
        y -= 6*mm

    # Total
    y -= 8*mm
    c.line(25*mm, y, 185*mm, y)
    y -= 10*mm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(30*mm, y, "TOTAL:")
    c.drawString(150*mm, y, "CZK 10,290")

    # No breakfast included - but expensive spa treatments on weekend
    y -= 15*mm
    c.setFont("Helvetica", 9)
    c.setFillColor(gray)
    c.drawString(30*mm, y, "Note: Weekend rate. No business center services available.")

    c.save()
    print(f"Created: {filepath}")
    return filepath


if __name__ == "__main__":
    create_breakfast_receipt()
    create_weekend_trip_docs()
    print("\nFraud detection demo documents created!")
    print("\nUsage:")
    print("  1. Upload hotel_folio_grand_wien.pdf + breakfast_receipt_fraud.pdf")
    print("     -> Triggers KB-RULE-01 (meal double-dipping)")
    print("")
    print("  2. Upload hotel_weekend_suspicious.pdf alone")
    print("     -> Triggers KB-RULE-02 (weekend travel anomaly)")
