# -*- coding: utf-8 -*-
"""
perdiemo_client.py — Zero-dependency client SDK for the PerDiemo REST API.

Provides structured access to statutory per diem calculations, ČNB daily
exchange rate anchoring, meal deduction logic, and SHA-256 cryptographic
verification signatures under Czech Labour Code Act No. 262/2006 Coll. (§§ 151-189).
"""
import os
import sys
import requests
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

load_dotenv()

DEFAULT_API_URL = os.environ.get("PERDIEMO_API_URL", "https://perdiemo-backend-production.onrender.com")

class PerDiemoClient:
    """Production client for PerDiemo statutory calculation and parsing API."""
    
    def __init__(self, base_url: str = DEFAULT_API_URL, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "PerDiemo-Hackathon-Client/1.0"
        })

    def health(self) -> Dict[str, Any]:
        """Verify API connectivity and fetch statutory country rate catalog."""
        url = f"{self.base_url}/"
        resp = self.session.get(url, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def parse_itinerary(self, text: str) -> Dict[str, Any]:
        """
        Parse natural language travel notes, Slack messages, or receipts into
        a structured statutory itinerary with automatic transport & breakfast detection.
        Works seamlessly with both English and Czech input prompts.
        """
        url = f"{self.base_url}/api/parse-itinerary"
        resp = self.session.post(url, json={"text": text}, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def calculate(
        self,
        trips: List[Dict[str, Any]],
        year: int = 2025,
        include_routes: bool = True
    ) -> Dict[str, Any]:
        """
        Calculate statutory domestic and foreign per diems, meal deductions,
        pocket money, ČNB exchange rates, and cryptographic verification signatures.
        """
        url = f"{self.base_url}/api/calculate"
        payload = {
            "year": year,
            "include_routes": include_routes,
            "trips": trips
        }
        resp = self.session.post(url, json=payload, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

if __name__ == "__main__":
    client = PerDiemoClient()
    print("Testing connection to PerDiemo Cloud Engine...")
    health = client.health()
    print(f"Status: {health.get('status')} | Service: {health.get('service')}")
    
    print("\nTesting natural language parse...")
    sample_text = (
        "Departed Prague on June 10, 2025 at 07:00 by company car to Vienna for client meetings. "
        "Crossed border at Mikulov at 09:30, arrived in Vienna at 11:00. Overnight at hotel with "
        "complimentary breakfast. On June 11 departed Vienna at 16:00, crossed border back into "
        "Czechia at 17:30, arrived in Prague at 20:00."
    )
    parsed = client.parse_itinerary(sample_text)
    print("Parsed purpose:", parsed.get("ucel_cesty"))
    print("Vehicle mode:", parsed.get("typ_vozidla"))
    print("Extracted legs:", len(parsed.get("itinerary", [])))

    print("\nCalculating statutory allowances...")
    calc_result = client.calculate(trips=[{
        "id_cesty": "HACKATHON-DEMO-001",
        "ucel_cesty": parsed.get("ucel_cesty", "Business"),
        "vlastnictvi_vozidla": parsed.get("typ_vozidla", "SLUZEBNI"),
        "zamestnanec_jednatel": "Alex Miller",
        "spolecnost": "Komerční banka Client a.s.",
        "bezplatna_strava": parsed.get("bezplatna_strava", {}),
        "itinerar": parsed.get("itinerary", [])
    }], year=2025)

    meta = calc_result.get("metadata", {})
    print(f"Total Stravné CZK: {meta.get('total_stravne_czk')} CZK")
    print(f"Total Kapesné CZK: {meta.get('total_kapesne_czk')} CZK")
    print(f"Meal Deductions CZK: {meta.get('total_kraceni_czk')} CZK")
    print(f"Audit SHA-256 Signature: {meta.get('verification_signature')}")
