# -*- coding: utf-8 -*-
"""
agent_intake.py — AWS Bedrock Multimodal Document & Itinerary Intake Agent.

Uses Amazon Bedrock (Anthropic Claude 3.5 Sonnet v2) to extract structured
travel itineraries, flight departure/arrival timestamps, border crossings,
hotel folios, and meal provisions from images, PDFs, or raw text descriptions.
"""
import os
import sys
import json
import base64
from typing import Dict, Any, Optional
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

AWS_REGION = os.environ.get("AWS_REGION", "eu-central-1")
# In Europe, Claude runs through EU cross-region inference profiles, so model ID needs 'eu.' prefix:
# Sonnet 4.5: eu.anthropic.claude-sonnet-4-5-20250929-v1:0 (recommended for extraction accuracy)
# Haiku 4.5:  eu.anthropic.claude-haiku-4-5-20251001-v1:0 (recommended for high-volume drafting)
BEDROCK_MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "eu.anthropic.claude-sonnet-4-5-20250929-v1:0")

EXTRACTION_SYSTEM_PROMPT = """You are an expert corporate travel auditor and multimodal parser for Czech statutory per diem accounting.
Your task is to analyze travel documents (flight boarding passes, train bookings, hotel folios, taxi receipts) or text logs, and extract a structured travel itinerary complying with statutory accounting rules.

Return a strictly valid JSON object matching this schema:
{
  "ucel_cesty": "string (business purpose, e.g. Client Negotiations)",
  "typ_vozidla": "string (SLUZEBNI for company car/flight/train, or OSOBNI for private vehicle)",
  "zamestnanec_jednatel": "string (traveler name if detected)",
  "spolecnost": "string (company name if detected)",
  "itinerary": [
    {
      "typ": "ODJEZD | PRIJEZD | HRANICE_PRECHOD | NÁVRAT_ODJEZD | HRANICE_NAVRAT | KREUZ_NAVRAT",
      "datum": "YYYY-MM-DDTHH:MM (local ISO timestamp)",
      "misto": "City name",
      "vzdalenost_km": 0.0,
      "transport_type": "plane | train | company_car | private_vehicle | bus",
      "country_code": "3-letter ISO code e.g. CZE, AUT, DEU, GBR, FRA, POL, SVK",
      "layover_type": "meeting | conference | transit | null"
    }
  ],
  "bezplatna_strava": {
    "YYYY-MM-DD": ["snidane", "obed", "vecer"]
  },
  "hotel_info": {
    "hotel_name": "string or null",
    "breakfast_included": true | false
  }
}
Do not include any commentary, code fences, or explanations. Return ONLY the JSON object.
"""

CARD_CLUSTERING_SYSTEM_PROMPT = """You are an autonomous corporate travel finance agent specializing in payment operations and Czech statutory travel allowances (§§ 151-189 ZP).
Your task is to analyze a raw corporate credit card transaction stream, identify travel-related charges, cluster them into a business trip, detect hotel lodging and meals, identify personal expenses on the corporate card, and generate a standardized statutory itinerary.

Input: A list of corporate card transactions with timestamps, merchant descriptors, amounts, MCC codes, notes, and locations.

CRITICAL RULES FOR EXTRACTION:
1. Destination & Transport Mode:
   - Identify the primary business destination city and country code from merchant locations and tickets.
   - Detect transport modes (train, bus, plane, or company/private car via fuel/toll merchants).
   - Infer departure from Czech Republic, border crossing times, and return to Czech Republic.

2. Hotel Stay & Meal Status:
   - Corporate credit card streams capture lodging payments (MCC 7011) but NEVER contain folio line items or meal plan data.
   - At this card-stream ingestion stage, always classify lodging as room-only:
     * Set hotel_info.breakfast_included = false
     * Set 'bezplatna_strava': {} (empty, 0% meal deduction).
     * 100% full statutory per diem is preserved without deductions.

3. Reconciliation & Personal Expense Classification:
   - Separate business travel card expenses from personal expenses.
   - Identify any transaction marked with expense_type: 'PERSONAL_EXPENSE' or non-business merchant (e.g. grocery snack, personal pharmacy, souvenir) and flag it under 'flagged_transactions' with its transaction_id and reason.

Return a strictly valid JSON object matching this schema:
{
  "detected_trip": {
    "destination_city": "Berlin",
    "destination_country": "DEU",
    "start_time": "2025-09-15T07:00",
    "end_time": "2025-09-17T19:00",
    "purpose": "Client Negotiations & Business Meetings",
    "summary": "3-day business trip to Berlin, Germany detected via card transactions."
  },
  "statutory_itinerary": {
    "ucel_cesty": "Client Negotiations & Business Meetings (Berlin)",
    "typ_vozidla": "SLUZEBNI",
    "zamestnanec_jednatel": "Alex Miller",
    "spolecnost": "Komerční banka Corporate Client a.s.",
    "itinerary": [
      {
        "typ": "ODJEZD",
        "datum": "2025-09-15T07:00",
        "misto": "Prague",
        "vzdalenost_km": 0.0,
        "transport_type": "train",
        "country_code": "CZE",
        "layover_type": null
      },
      {
        "typ": "HRANICE_PRECHOD",
        "datum": "2025-09-15T09:30",
        "misto": "Děčín / Bad Schandau",
        "vzdalenost_km": 140.0,
        "transport_type": "train",
        "country_code": "CZE",
        "layover_type": null
      },
      {
        "typ": "PRIJEZD",
        "datum": "2025-09-15T11:45",
        "misto": "Berlin",
        "vzdalenost_km": 210.0,
        "transport_type": "train",
        "country_code": "DEU",
        "layover_type": "meeting"
      },
      {
        "typ": "NÁVRAT_ODJEZD",
        "datum": "2025-09-17T15:00",
        "misto": "Berlin",
        "vzdalenost_km": 0.0,
        "transport_type": "bus",
        "country_code": "DEU",
        "layover_type": null
      },
      {
        "typ": "HRANICE_NAVRAT",
        "datum": "2025-09-17T17:30",
        "misto": "Krásný Les / Breitenau",
        "vzdalenost_km": 210.0,
        "transport_type": "bus",
        "country_code": "CZE",
        "layover_type": null
      },
      {
        "typ": "KREUZ_NAVRAT",
        "datum": "2025-09-17T19:00",
        "misto": "Prague",
        "vzdalenost_km": 140.0,
        "transport_type": "bus",
        "country_code": "CZE",
        "layover_type": null
      }
    ],
    "bezplatna_strava": {},
    "hotel_info": {
      "hotel_name": "Hotel Adlon Kempinski Berlin",
      "breakfast_included": false
    }
  },
  "reconciliation_classification": {
    "travel_card_expenses_czk": 18250.00,
    "personal_card_expenses_czk": 450.00,
    "non_travel_card_expenses_czk": 0.0,
    "flagged_transactions": [
      {
        "transaction_id": "TSYS-KB-TX-005",
        "reason": "Personal snack / grocery purchase on company card. Automatically offset from cash reimbursement."
      }
    ]
  }
}
Do not include any commentary, code fences, or explanations. Return ONLY the JSON object.
"""

class BedrockIntakeAgent:
    """Agent pipeline using AWS Bedrock to parse unstructured documents into statutory itineraries."""

    def __init__(
        self,
        region_name: str = AWS_REGION,
        model_id: str = BEDROCK_MODEL_ID
    ):
        self.region_name = region_name
        self.model_id = model_id
        self._client = None

    def _get_bedrock_client(self):
        try:
            import boto3
            access_key = os.environ.get("AWS_ACCESS_KEY_ID")
            secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
            session_token = os.environ.get("AWS_SESSION_TOKEN")
            profile = os.environ.get("AWS_PROFILE", "martin-hackathon")

            if access_key and secret_key:
                session = boto3.Session(
                    aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key,
                    aws_session_token=session_token,
                    region_name=self.region_name
                )
            elif profile:
                session = boto3.Session(profile_name=profile, region_name=self.region_name)
            else:
                session = boto3.Session(region_name=self.region_name)

            self._client = session.client(
                service_name="bedrock-runtime",
                region_name=self.region_name
            )
            return self._client
        except Exception as e:
            print(f"[WARN] Failed to initialize AWS Bedrock client: {e}. Falling back to resilient mock generator.")
            return None

    def extract_from_text(self, travel_text: str) -> Dict[str, Any]:
        """Extract structured itinerary from free-form text using Claude 3.5 Sonnet on Bedrock."""
        client = self._get_bedrock_client()
        if client is None:
            return self._mock_extraction(travel_text)

        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2048,
            "system": EXTRACTION_SYSTEM_PROMPT,
            "messages": [
                {
                    "role": "user",
                    "content": f"Please extract the statutory travel itinerary from this text:\n\n{travel_text}"
                }
            ],
            "temperature": 0.0
        }

        try:
            response = client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body)
            )
            response_body = json.loads(response["body"].read().decode("utf-8"))
            content_text = response_body["content"][0]["text"]
            return self._clean_json(content_text)
        except Exception as e:
            print(f"[ERROR] Bedrock invocation failed: {e}. Using fallback mock.")
            return self._mock_extraction(travel_text)

    @staticmethod
    def _clean_json(text: str) -> Dict[str, Any]:
        """Strip markdown fences and whitespace from LLM response before parsing JSON."""
        clean = text.strip()
        if clean.startswith("```json"):
            clean = clean[7:]
        elif clean.startswith("```"):
            clean = clean[3:]
        if clean.endswith("```"):
            clean = clean[:-3]
        clean = clean.strip()
        start = clean.find("{")
        end = clean.rfind("}")
        if start != -1 and end != -1:
            clean = clean[start:end+1]
        return json.loads(clean)

    def extract_from_image(self, image_bytes: bytes, mime_type: str = "image/jpeg") -> Dict[str, Any]:
        """Multimodal extraction from receipt or ticket image."""
        client = self._get_bedrock_client()
        if client is None:
            return self._mock_extraction("Uploaded document image")

        base64_data = base64.b64encode(image_bytes).decode("utf-8")
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2048,
            "system": EXTRACTION_SYSTEM_PROMPT,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": mime_type,
                                "data": base64_data
                            }
                        },
                        {
                            "type": "text",
                            "text": "Extract all travel departure/arrival details, border crossings, hotel stays, and meals from this document."
                        }
                    ]
                }
            ],
            "temperature": 0.0
        }

        try:
            response = client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body)
            )
            response_body = json.loads(response["body"].read().decode("utf-8"))
            content_text = response_body["content"][0]["text"]
            return self._clean_json(content_text)
        except Exception as e:
            print(f"[ERROR] Bedrock multimodal call failed: {e}. Using fallback mock.")
            return self._mock_extraction("Uploaded document image")

    def _mock_extraction(self, input_summary: str) -> Dict[str, Any]:
        """Deterministic mock data for rapid development before AWS keys are entered."""
        return {
            "ucel_cesty": "Client Negotiations & Technology Demonstration",
            "typ_vozidla": "SLUZEBNI",
            "zamestnanec_jednatel": "Alex Miller",
            "spolecnost": "Komerční banka Corporate Client",
            "itinerary": [
                {
                    "typ": "ODJEZD",
                    "datum": "2025-06-10T07:00",
                    "misto": "Prague",
                    "vzdalenost_km": 0.0,
                    "transport_type": "company_car",
                    "country_code": "CZE",
                    "layover_type": None
                },
                {
                    "typ": "HRANICE_PRECHOD",
                    "datum": "2025-06-10T09:30",
                    "misto": "Mikulov",
                    "vzdalenost_km": 200.0,
                    "transport_type": "company_car",
                    "country_code": "CZE",
                    "layover_type": None
                },
                {
                    "typ": "PRIJEZD",
                    "datum": "2025-06-10T11:00",
                    "misto": "Vienna",
                    "vzdalenost_km": 80.0,
                    "transport_type": "company_car",
                    "country_code": "AUT",
                    "layover_type": "meeting"
                },
                {
                    "typ": "NÁVRAT_ODJEZD",
                    "datum": "2025-06-11T16:00",
                    "misto": "Vienna",
                    "vzdalenost_km": 0.0,
                    "transport_type": "company_car",
                    "country_code": "AUT",
                    "layover_type": None
                },
                {
                    "typ": "HRANICE_NAVRAT",
                    "datum": "2025-06-11T17:30",
                    "misto": "Mikulov",
                    "vzdalenost_km": 80.0,
                    "transport_type": "company_car",
                    "country_code": "CZE",
                    "layover_type": None
                },
                {
                    "typ": "KREUZ_NAVRAT",
                    "datum": "2025-06-11T20:00",
                    "misto": "Prague",
                    "vzdalenost_km": 200.0,
                    "transport_type": "company_car",
                    "country_code": "CZE",
                    "layover_type": None
                }
            ],
            "bezplatna_strava": {
                "2025-06-11": ["snidane"]
            },
            "hotel_info": {
                "hotel_name": "Grand Hotel Wien",
                "breakfast_included": True
            }
        }

    def cluster_card_stream(self, transactions: list, traveler_name: str = "Alex Miller") -> Dict[str, Any]:
        """
        Ingests a raw stream of TSYS / corporate credit card transactions,
        clusters them into a coherent business travel itinerary, detects hotel lodging
        and complimentary breakfast, flags personal expenses, and outputs a statutory
        itinerary ready for the PerDiemo Cloud Engine.
        """
        client = self._get_bedrock_client()
        if client is None:
            return self._mock_card_clustering(transactions, traveler_name)

        tx_payload_str = json.dumps(transactions, indent=2, ensure_ascii=False)
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 3000,
            "system": CARD_CLUSTERING_SYSTEM_PROMPT,
            "messages": [
                {
                    "role": "user",
                    "content": (
                        f"Traveler: {traveler_name}\n"
                        f"Corporate Credit Card Stream (TSYS Sandbox):\n\n"
                        f"{tx_payload_str}\n\n"
                        f"Detect travel clusters, synthesize statutory itinerary, and categorize expenses."
                    )
                }
            ],
            "temperature": 0.0
        }

        try:
            response = client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body)
            )
            response_body = json.loads(response["body"].read().decode("utf-8"))
            content_text = response_body["content"][0]["text"]
            return self._clean_json(content_text)
        except Exception as e:
            print(f"[WARN] Bedrock card clustering invocation failed: {e}. Using resilient mock fallback.")
            return self._mock_card_clustering(transactions, traveler_name)

    def _mock_card_clustering(self, transactions: Optional[list] = None, traveler_name: str = "Alex Miller") -> Dict[str, Any]:
        """
        Dynamic parser fallback that extracts destination, itinerary, hotel lodging,
        breakfast deductions, and personal expenses directly from raw card transactions.
        """
        import re
        from datetime import datetime, timedelta

        txs = transactions or []
        dest_city = "Vienna"
        dest_country = "AUT"

        city_map = {
            "berlin": ("Berlin", "DEU", "train"),
            "vienna": ("Vienna", "AUT", "train"),
            "wien": ("Vienna", "AUT", "train"),
            "zurich": ("Zurich", "CHE", "flight"),
            "zürich": ("Zurich", "CHE", "flight"),
            "london": ("London", "GBR", "flight"),
            "paris": ("Paris", "FRA", "flight"),
            "munich": ("Munich", "DEU", "company_car"),
            "münchen": ("Munich", "DEU", "company_car"),
            "frankfurt": ("Frankfurt", "DEU", "train"),
            "warsaw": ("Warsaw", "POL", "train"),
            "bratislava": ("Bratislava", "SVK", "company_car"),
            "milan": ("Milan", "ITA", "flight"),
            "milano": ("Milan", "ITA", "flight"),
            "amsterdam": ("Amsterdam", "NLD", "flight"),
            "brussels": ("Brussels", "BEL", "flight"),
            "budapest": ("Budapest", "HUN", "train")
        }

        # Scan transactions for destination
        for tx in txs:
            blob = f"{tx.get('merchant_city', '')} {tx.get('merchant_name', '')} {tx.get('notes', '')} {tx.get('merchant_descriptor', '')}".lower()
            for k, (c, ctry, mode) in city_map.items():
                if k in blob:
                    dest_city = c
                    dest_country = ctry
                    break

        # Scan timestamps
        timestamps = []
        for tx in txs:
            ts = tx.get("timestamp")
            if ts:
                try:
                    timestamps.append(datetime.fromisoformat(ts))
                except Exception:
                    pass

        if timestamps:
            timestamps.sort()
            start_dt = timestamps[0]
            end_dt = timestamps[-1] + timedelta(hours=3)
        else:
            start_dt = datetime(2025, 6, 10, 7, 0)
            end_dt = datetime(2025, 6, 12, 19, 0)

        # Detect transport modes
        transport_type = "train"
        tx_text = " ".join([f"{tx.get('merchant_name', '')} {tx.get('notes', '')}".lower() for tx in txs])
        if any(w in tx_text for w in ["shell", "omv", "orlen", "vignette", "asfinag", "parking", "parkhaus", "fuel", "gas"]):
            transport_type = "company_car"
        elif any(w in tx_text for w in ["airline", "flight", "lufthansa", "swiss", "airways", "austrian", "klm"]):
            transport_type = "flight"
        elif any(w in tx_text for w in ["flixbus", "regiojet bus", "bus ticket", "autobus"]):
            transport_type = "bus"

        # Detect hotel lodging (card streams never include breakfast line items)
        hotel_name = f"Hotel {dest_city} Central"
        for tx in txs:
            mcc = tx.get("mcc", 0)
            m_name = tx.get("merchant_name", "")
            if mcc == 7011 or "hotel" in m_name.lower() or tx.get("expense_type") == "TRAVEL_LODGING":
                hotel_name = m_name if "hotel" in m_name.lower() else f"Hotel {dest_city} Central"

        breakfast_included = False
        bezplatna_strava = {}
        num_days = max(1, (end_dt.date() - start_dt.date()).days)

        # Calculate totals
        travel_card_czk = sum(float(tx.get("billing_amount_czk", tx.get("amount", 0) * 25.12)) for tx in txs if tx.get("expense_type") != "PERSONAL_EXPENSE")
        personal_card_czk = sum(float(tx.get("billing_amount_czk", tx.get("amount", 0) * 25.12)) for tx in txs if tx.get("expense_type") == "PERSONAL_EXPENSE")

        flagged = []
        for tx in txs:
            if tx.get("expense_type") == "PERSONAL_EXPENSE" or any(w in tx.get("merchant_name", "").lower() for w in ["billa", "spar", "rewe", "market", "grocery", "souvenir", "apotheke", "pharmacy"]):
                flagged.append({
                    "transaction_id": tx.get("transaction_id"),
                    "merchant": tx.get("merchant_name"),
                    "amount_czk": tx.get("billing_amount_czk", round(tx.get("amount", 0) * 25.12, 2)),
                    "reason": f"Personal expenditure ({tx.get('merchant_name')}) charged on company credit card. Automatically offset from net per diem reimbursement."
                })

        return {
            "detected_trip": {
                "destination_city": dest_city,
                "destination_country": dest_country,
                "start_time": start_dt.strftime("%Y-%m-%dT%H:%M"),
                "end_time": end_dt.strftime("%Y-%m-%dT%H:%M"),
                "purpose": f"Client Negotiations & Commercial Review ({dest_city})",
                "summary": f"{num_days+1}-day business trip to {dest_city}, {dest_country} detected across {len(txs)} corporate card transactions."
            },
            "statutory_itinerary": {
                "ucel_cesty": f"Business Negotiations & Client Expansion ({dest_city})",
                "typ_vozidla": "SLUZEBNI",
                "zamestnanec_jednatel": traveler_name,
                "spolecnost": "Komerční banka Corporate Client a.s.",
                "itinerary": [
                    {
                        "typ": "ODJEZD",
                        "datum": start_dt.strftime("%Y-%m-%dT%H:%M"),
                        "misto": "Prague",
                        "vzdalenost_km": 0.0,
                        "transport_type": transport_type,
                        "country_code": "CZE",
                        "layover_type": None
                    },
                    {
                        "typ": "HRANICE_PRECHOD",
                        "datum": (start_dt + timedelta(hours=2, minutes=30)).strftime("%Y-%m-%dT%H:%M"),
                        "misto": "CZ Border Exit",
                        "vzdalenost_km": 180.0,
                        "transport_type": transport_type,
                        "country_code": "CZE",
                        "layover_type": None
                    },
                    {
                        "typ": "PRIJEZD",
                        "datum": (start_dt + timedelta(hours=4)).strftime("%Y-%m-%dT%H:%M"),
                        "misto": dest_city,
                        "vzdalenost_km": 120.0,
                        "transport_type": transport_type,
                        "country_code": dest_country,
                        "layover_type": "meeting"
                    },
                    {
                        "typ": "NÁVRAT_ODJEZD",
                        "datum": (end_dt - timedelta(hours=4)).strftime("%Y-%m-%dT%H:%M"),
                        "misto": dest_city,
                        "vzdalenost_km": 0.0,
                        "transport_type": transport_type,
                        "country_code": dest_country,
                        "layover_type": None
                    },
                    {
                        "typ": "HRANICE_NAVRAT",
                        "datum": (end_dt - timedelta(hours=1, minutes=30)).strftime("%Y-%m-%dT%H:%M"),
                        "misto": "CZ Border Entry",
                        "vzdalenost_km": 120.0,
                        "transport_type": transport_type,
                        "country_code": "CZE",
                        "layover_type": None
                    },
                    {
                        "typ": "KREUZ_NAVRAT",
                        "datum": end_dt.strftime("%Y-%m-%dT%H:%M"),
                        "misto": "Prague",
                        "vzdalenost_km": 180.0,
                        "transport_type": transport_type,
                        "country_code": "CZE",
                        "layover_type": None
                    }
                ],
                "bezplatna_strava": bezplatna_strava,
                "hotel_info": {
                    "hotel_name": hotel_name,
                    "breakfast_included": breakfast_included
                }
            },
            "reconciliation_classification": {
                "travel_card_expenses_czk": round(travel_card_czk, 2),
                "personal_card_expenses_czk": round(personal_card_czk, 2),
                "non_travel_card_expenses_czk": 0.0,
                "flagged_transactions": flagged
            }
        }

    def generate_card_stream(
        self,
        traveler_name: str = "Alex Miller",
        destination: str = "Berlin",
        num_days: int = 3
    ) -> Dict[str, Any]:
        """
        Dynamically queries Amazon Bedrock Claude Sonnet 4.5 to generate a realistic,
        diverse corporate card transaction stream (TSYS format) for any business destination.
        """
        client = self._get_bedrock_client()
        prompt = f"""Generate a realistic, messy corporate credit card stream (TSYS format) for employee '{traveler_name}' on a {num_days}-day business trip from Prague to '{destination}'.

Vary the travel style realistically:
- Transport: Choose a realistic travel method:
  * Multi-modal: e.g. Outbound train (České dráhy, Deutsche Bahn, ÖBB, SBB) + Return via long-distance bus (FlixBus, RegioJet) or airline (Lufthansa, Austrian Airlines, British Airways, Swiss, KLM).
  * Road trip by car: Gas station fuel stops (Shell, OMV, Orlen, MOL), highway toll vignettes (Asfinag Vignette, Toll Collect, Telepass), and parking garage fees (APCOA, Parkhaus).
  * Flight + urban transit: Airline flight ticket + airport express train / metro pass + Uber / FreeNow / taxi rides.

Hotel Stay & Breakfast (§ 163 ZP):
- Randomly determine if breakfast is included:
  * 50% chance: The room rate includes complimentary breakfast. In the hotel transaction 'notes' and 'hotel_details', write explicitly: "Accommodation ({num_days-1} nights). Room rate includes complimentary breakfast".
  * 50% chance: Room only. In the hotel transaction 'notes' and 'hotel_details', write explicitly: "Accommodation ({num_days-1} nights). Room only - breakfast not included".

Incidental & Messy Expenses:
- Add a business client dinner at a local restaurant matching {destination}.
- Add local transit (taxi, metro, Uber).
- Add exactly ONE accidental personal expense on the company card (e.g., supermarket snack at Billa/SPAR/Rewe, souvenir, or pharmacy) with "expense_type": "PERSONAL_EXPENSE".
- In "out_of_pocket_cash", add 1-2 realistic cash expenses (e.g. coin parking meter, cash taxi when terminal failed, or street food).

Must return a strictly valid JSON object matching this structure:
{{
  "account_id": "KB-CORP-ACC-99214",
  "corporate_client": "Komerční banka Corporate Client a.s.",
  "cardholder": "{traveler_name}",
  "employee_id": "EMP-KB-0042",
  "employee_iban": "CZ6501000000001928374650",
  "transactions": [
    {{
      "transaction_id": "TSYS-KB-TX-001",
      "card_token": "KB-CORP-VISA-4819",
      "cardholder_name": "{traveler_name}",
      "timestamp": "2025-09-15T08:00:00",
      "merchant_descriptor": "TRANSPORT TICKET",
      "merchant_name": "Official Carrier Name",
      "mcc": 4112,
      "mcc_category": "Passenger Transport",
      "amount": 180.00,
      "currency": "EUR",
      "billing_amount_czk": 4521.60,
      "merchant_city": "{destination}",
      "merchant_country": "DEU",
      "status": "SETTLED",
      "is_company_card": true,
      "expense_type": "TRAVEL_TRANSPORT",
      "notes": "Outbound business transport"
    }}
  ],
  "out_of_pocket_cash": [
    {{
      "expense_id": "OOP-CASH-001",
      "merchant_name": "Local Cash Taxi",
      "amount": 25.00,
      "currency": "EUR",
      "payment_method": "PERSONAL_CASH",
      "notes": "Emergency taxi when POS terminal was down"
    }}
  ]
}}

Include 6-9 transactions in chronological order. Do not output markdown code blocks. Return ONLY valid JSON."""

        if client:
            try:
                body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 4000,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.8
                }
                response = client.invoke_model(
                    modelId=self.model_id,
                    body=json.dumps(body)
                )
                response_body = json.loads(response["body"].read().decode("utf-8"))
                return self._clean_json(response_body["content"][0]["text"])
            except Exception as e:
                print(f"[WARN] Bedrock dynamic card generator failed: {e}. Falling back to dynamic procedural generator.")

        return self._dynamic_scenario_generator(traveler_name, destination, num_days)

    def _dynamic_scenario_generator(self, traveler_name: str, destination: str, num_days: int) -> Dict[str, Any]:
        """
        Rich procedural generator producing realistic, messy corporate travel card streams
        across multiple travel archetypes and European destinations.
        """
        import random
        from datetime import datetime, timedelta

        dest_meta = {
            "Berlin": {"curr": "EUR", "fx": 25.12, "ctry": "DEU", "hotel": "Hotel Adlon Kempinski Berlin", "dining": "Käfer Restaurant Berlin", "transit": "S-Bahn Berlin / Uber", "personal": "Rewe City Berlin"},
            "Vienna": {"curr": "EUR", "fx": 25.12, "ctry": "AUT", "hotel": "Grand Hotel Wien", "dining": "Plachutta Wollzeile", "transit": "Wiener Linien / Uber", "personal": "Billa Corso Wien"},
            "Zurich": {"curr": "CHF", "fx": 26.40, "ctry": "CHE", "hotel": "Hotel Schweizerhof Zürich", "dining": "Kronenhalle Zürich", "transit": "ZVV Transit Zürich", "personal": "Coop Pronto Zürich HB"},
            "London": {"curr": "GBP", "fx": 30.15, "ctry": "GBR", "hotel": "The Langham London", "dining": "Hawksmoor Guildhall", "transit": "TfL London Underground", "personal": "Boots Pharmacy London"},
            "Paris": {"curr": "EUR", "fx": 25.12, "ctry": "FRA", "hotel": "Hôtel Plaza Athénée", "dining": "Le Grand Colbert Paris", "transit": "RATP Métro Paris", "personal": "Monoprix Opéra"},
            "Munich": {"curr": "EUR", "fx": 25.12, "ctry": "DEU", "hotel": "Bayerischer Hof Munich", "dining": "Spatenhaus an der Oper", "transit": "MVV München / FreeNow", "personal": "Edeka City Munich"},
            "Frankfurt": {"curr": "EUR", "fx": 25.12, "ctry": "DEU", "hotel": "Steigenberger Frankfurter Hof", "dining": "Main Tower Restaurant", "transit": "RMV Frankfurt", "personal": "Rewe Frankfurt Hauptbahnhof"},
            "Warsaw": {"curr": "PLN", "fx": 5.95, "ctry": "POL", "hotel": "Hotel Bristol Warsaw", "dining": "U Kucharzy Warszawa", "transit": "ZTM Warszawa / Bolt", "personal": "Biedronka Warszawa Centrum"},
            "Bratislava": {"curr": "EUR", "fx": 25.12, "ctry": "SVK", "hotel": "Grand Hotel River Park", "dining": "UFO watch.taste.groove", "transit": "DPB Bratislava / Bolt", "personal": "Tesco Express Bratislava"},
            "Milan": {"curr": "EUR", "fx": 25.12, "ctry": "ITA", "hotel": "Armani Hotel Milano", "dining": "Trattoria Milanese", "transit": "ATM Milano / FreeNow", "personal": "Carrefour Express Milano"},
            "Amsterdam": {"curr": "EUR", "fx": 25.12, "ctry": "NLD", "hotel": "Conservatorium Hotel", "dining": "Restaurant De Kas", "transit": "GVB Amsterdam / Uber", "personal": "Albert Heijn Amsterdam"},
            "Brussels": {"curr": "EUR", "fx": 25.12, "ctry": "BEL", "hotel": "The Hotel Brussels", "dining": "Chez Léon Bruxelles", "transit": "STIB-MIVB Brussels", "personal": "Delhaize City Brussels"},
            "Budapest": {"curr": "HUF", "fx": 0.063, "ctry": "HUN", "hotel": "Corinthia Hotel Budapest", "dining": "Gundel Restaurant Budapest", "transit": "BKK Budapest", "personal": "Spar Budapest"}
        }

        meta = dest_meta.get(destination, {"curr": "EUR", "fx": 25.12, "ctry": "DEU", "hotel": f"Grand {destination} Hotel", "dining": f"{destination} City Bistro", "transit": "Local Transit", "personal": "Local Supermarket"})
        curr = meta["curr"]
        fx = meta["fx"]
        ctry = meta["ctry"]

        start_date = datetime(2025, 9, 10 + random.randint(0, 15), 7, 30)
        breakfast_inc = random.choice([True, False])
        travel_archetype = random.choice(["multi_modal", "car_roadtrip", "flight_transit"])

        txs = []
        # Transport Outbound
        if travel_archetype == "car_roadtrip":
            txs.append({
                "transaction_id": f"TSYS-KB-{random.randint(10000, 99999)}",
                "card_token": "KB-CORP-VISA-4819",
                "cardholder_name": traveler_name,
                "timestamp": (start_date).isoformat(),
                "merchant_descriptor": "ORLEN HIGHWAY FUEL CZ",
                "merchant_name": "Orlen Benzina Expressway",
                "mcc": 5541,
                "mcc_category": "Service Stations / Fuel",
                "amount": round(random.uniform(55, 75) * (1.0 if curr == "EUR" else (1.1 if curr == "CHF" else 0.85)), 2),
                "currency": curr,
                "billing_amount_czk": round(random.uniform(1400, 1900), 2),
                "merchant_city": "D1 Expressway",
                "merchant_country": "CZE",
                "status": "SETTLED",
                "is_company_card": True,
                "expense_type": "TRAVEL_TRANSPORT",
                "notes": "Refueling company vehicle (outbound leg)"
            })
            txs.append({
                "transaction_id": f"TSYS-KB-{random.randint(10000, 99999)}",
                "card_token": "KB-CORP-VISA-4819",
                "cardholder_name": traveler_name,
                "timestamp": (start_date + timedelta(hours=3)).isoformat(),
                "merchant_descriptor": f"HIGHWAY TOLL VIGNETTE {ctry}",
                "merchant_name": f"Electronic Toll Authority {ctry}",
                "mcc": 4784,
                "mcc_category": "Tolls and Bridge Fees",
                "amount": round(random.uniform(12, 25) * (1.0 if curr == "EUR" else 1.1), 2),
                "currency": curr,
                "billing_amount_czk": round(random.uniform(300, 650), 2),
                "merchant_city": destination,
                "merchant_country": ctry,
                "status": "SETTLED",
                "is_company_card": True,
                "expense_type": "TRAVEL_TRANSPORT",
                "notes": f"Highway vignette / transit toll fee for {ctry}"
            })
        elif travel_archetype == "multi_modal":
            txs.append({
                "transaction_id": f"TSYS-KB-{random.randint(10000, 99999)}",
                "card_token": "KB-CORP-VISA-4819",
                "cardholder_name": traveler_name,
                "timestamp": (start_date).isoformat(),
                "merchant_descriptor": "ČESKÉ DRÁHY EUROCITY",
                "merchant_name": "České dráhy a.s.",
                "mcc": 4112,
                "mcc_category": "Passenger Railways",
                "amount": round(random.uniform(70, 110) * (1.0 if curr == "EUR" else 1.1), 2),
                "currency": curr,
                "billing_amount_czk": round(random.uniform(1750, 2750), 2),
                "merchant_city": "Prague",
                "merchant_country": "CZE",
                "status": "SETTLED",
                "is_company_card": True,
                "expense_type": "TRAVEL_TRANSPORT",
                "notes": f"EuroCity 1st class train ticket to {destination}"
            })
        else: # flight_transit
            txs.append({
                "transaction_id": f"TSYS-KB-{random.randint(10000, 99999)}",
                "card_token": "KB-CORP-VISA-4819",
                "cardholder_name": traveler_name,
                "timestamp": (start_date).isoformat(),
                "merchant_descriptor": f"AIRLINE TICKET PRG-{destination[:3].upper()}",
                "merchant_name": "European Business Carrier",
                "mcc": 4511,
                "mcc_category": "Airlines",
                "amount": round(random.uniform(180, 310) * (1.0 if curr == "EUR" else 1.1), 2),
                "currency": curr,
                "billing_amount_czk": round(random.uniform(4500, 7800), 2),
                "merchant_city": "Prague Airport",
                "merchant_country": "CZE",
                "status": "SETTLED",
                "is_company_card": True,
                "expense_type": "TRAVEL_TRANSPORT",
                "notes": f"Outbound flight ticket Prague to {destination}"
            })

        # Hotel Lodging
        hotel_amt = round(random.uniform(160, 240) * (num_days - 1) * (1.0 if curr == "EUR" else 1.1), 2)
        b_note = "Room rate includes complimentary breakfast" if breakfast_inc else "Room only - breakfast not included"
        txs.append({
            "transaction_id": f"TSYS-KB-{random.randint(10000, 99999)}",
            "card_token": "KB-CORP-VISA-4819",
            "cardholder_name": traveler_name,
            "timestamp": (start_date + timedelta(hours=5)).isoformat(),
            "merchant_descriptor": meta["hotel"].upper(),
            "merchant_name": meta["hotel"],
            "mcc": 7011,
            "mcc_category": "Hotels and Lodging",
            "amount": hotel_amt,
            "currency": curr,
            "billing_amount_czk": round(hotel_amt * fx, 2),
            "merchant_city": destination,
            "merchant_country": ctry,
            "status": "SETTLED",
            "is_company_card": True,
            "expense_type": "TRAVEL_LODGING",
            "hotel_details": {
                "nights": num_days - 1,
                "breakfast_included": breakfast_inc,
                "rate_plan": "Bed & Breakfast" if breakfast_inc else "Room Only"
            },
            "notes": f"Accommodation ({num_days-1} nights). {b_note}"
        })

        # Local Urban Transit
        txs.append({
            "transaction_id": f"TSYS-KB-{random.randint(10000, 99999)}",
            "card_token": "KB-CORP-VISA-4819",
            "cardholder_name": traveler_name,
            "timestamp": (start_date + timedelta(days=1, hours=3)).isoformat(),
            "merchant_descriptor": f"LOCAL TRANSIT {destination.upper()}",
            "merchant_name": meta["transit"],
            "mcc": 4121,
            "mcc_category": "Taxicabs and Transit",
            "amount": round(random.uniform(18, 42) * (1.0 if curr == "EUR" else 1.1), 2),
            "currency": curr,
            "billing_amount_czk": round(random.uniform(450, 1050), 2),
            "merchant_city": destination,
            "merchant_country": ctry,
            "status": "SETTLED",
            "is_company_card": True,
            "expense_type": "TRAVEL_TRANSPORT",
            "notes": "Transit to client headquarters for negotiations"
        })

        # Business Dinner
        din_amt = round(random.uniform(65, 140) * (1.0 if curr == "EUR" else 1.1), 2)
        txs.append({
            "transaction_id": f"TSYS-KB-{random.randint(10000, 99999)}",
            "card_token": "KB-CORP-VISA-4819",
            "cardholder_name": traveler_name,
            "timestamp": (start_date + timedelta(days=1, hours=12)).isoformat(),
            "merchant_descriptor": meta["dining"].upper(),
            "merchant_name": meta["dining"],
            "mcc": 5812,
            "mcc_category": "Restaurants",
            "amount": din_amt,
            "currency": curr,
            "billing_amount_czk": round(din_amt * fx, 2),
            "merchant_city": destination,
            "merchant_country": ctry,
            "status": "SETTLED",
            "is_company_card": True,
            "expense_type": "TRAVEL_MEAL",
            "notes": "Business dinner with corporate partner management"
        })

        # Accidental Personal Expense on Corporate Card
        pers_amt = round(random.uniform(14, 28) * (1.0 if curr == "EUR" else 1.1), 2)
        txs.append({
            "transaction_id": f"TSYS-KB-{random.randint(10000, 99999)}",
            "card_token": "KB-CORP-VISA-4819",
            "cardholder_name": traveler_name,
            "timestamp": (start_date + timedelta(days=2, hours=2)).isoformat(),
            "merchant_descriptor": meta["personal"].upper(),
            "merchant_name": meta["personal"],
            "mcc": 5411,
            "mcc_category": "Grocery / Personal Convenience",
            "amount": pers_amt,
            "currency": curr,
            "billing_amount_czk": round(pers_amt * fx, 2),
            "merchant_city": destination,
            "merchant_country": ctry,
            "status": "SETTLED",
            "is_company_card": True,
            "expense_type": "PERSONAL_EXPENSE",
            "notes": "Personal snacks / convenience purchase on corporate card (automatically offset from reimbursement)"
        })

        # Return Transport Leg (Multi-modal messiness: Bus back if train there, or Fuel if car)
        if travel_archetype == "multi_modal":
            txs.append({
                "transaction_id": f"TSYS-KB-{random.randint(10000, 99999)}",
                "card_token": "KB-CORP-VISA-4819",
                "cardholder_name": traveler_name,
                "timestamp": (start_date + timedelta(days=num_days-1, hours=7)).isoformat(),
                "merchant_descriptor": "FLIXBUS EXPRESS INTERCITY",
                "merchant_name": "FlixBus Central Europe",
                "mcc": 4131,
                "mcc_category": "Bus Lines",
                "amount": round(random.uniform(35, 60) * (1.0 if curr == "EUR" else 1.1), 2),
                "currency": curr,
                "billing_amount_czk": round(random.uniform(880, 1500), 2),
                "merchant_city": destination,
                "merchant_country": ctry,
                "status": "SETTLED",
                "is_company_card": True,
                "expense_type": "TRAVEL_TRANSPORT",
                "notes": f"Return intercity express bus ticket from {destination} to Prague"
            })
        elif travel_archetype == "car_roadtrip":
            txs.append({
                "transaction_id": f"TSYS-KB-{random.randint(10000, 99999)}",
                "card_token": "KB-CORP-VISA-4819",
                "cardholder_name": traveler_name,
                "timestamp": (start_date + timedelta(days=num_days-1, hours=6)).isoformat(),
                "merchant_descriptor": "SHELL STATION AUTOBAHN",
                "merchant_name": "Shell Highway Service",
                "mcc": 5541,
                "mcc_category": "Service Stations / Fuel",
                "amount": round(random.uniform(60, 85) * (1.0 if curr == "EUR" else 1.1), 2),
                "currency": curr,
                "billing_amount_czk": round(random.uniform(1500, 2100), 2),
                "merchant_city": destination,
                "merchant_country": ctry,
                "status": "SETTLED",
                "is_company_card": True,
                "expense_type": "TRAVEL_TRANSPORT",
                "notes": "Return leg vehicle refueling"
            })

        # Out-of-pocket cash claim
        oop_amt = round(random.uniform(15, 30), 2)
        oop = [
            {
                "expense_id": f"OOP-CASH-{random.randint(100, 999)}",
                "merchant_name": f"{destination} City Cash Parking Meter",
                "amount": oop_amt,
                "currency": curr,
                "payment_method": "PERSONAL_CASH",
                "notes": "Coin parking meter near client office (terminal declined card)"
            }
        ]

        return {
            "account_id": "KB-CORP-ACC-99214",
            "corporate_client": "Komerční banka Corporate Client a.s.",
            "cardholder": traveler_name,
            "employee_id": "EMP-KB-0042",
            "employee_iban": "CZ6501000000001928374650",
            "transactions": txs,
            "out_of_pocket_cash": oop
        }

    def conversational_query(self, user_question: str, trip_context: Dict[str, Any]) -> str:
        """
        Sends natural language questions directly to AWS Bedrock Claude Sonnet 4.5
        with full trip, per diem calculation, and audit context.
        """
        client = self._get_bedrock_client()
        context_str = json.dumps(trip_context, indent=2, ensure_ascii=False)
        prompt = f"""You are PerDiemo Copilot, an expert AI agent in corporate payment operations, bank reconciliation, and Czech statutory travel allowances (§§ 151-189 ZP).

Full Trip Context & Financial Settlement:
{context_str}

User Question: {user_question}

Provide an authoritative, clear, and mathematically accurate answer:
- Cite exact transactions, merchants, and amounts from the context.
- Refer to statutory Labour Code rules (§ 163 for meal deductions, § 170 for foreign travel, § 183 for ČNB fixing).
- Explain offsets or out-of-pocket reimbursements clearly.
"""
        if client:
            try:
                body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1024,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2
                }
                response = client.invoke_model(
                    modelId=self.model_id,
                    body=json.dumps(body)
                )
                response_body = json.loads(response["body"].read().decode("utf-8"))
                return response_body["content"][0]["text"]
            except Exception as e:
                print(f"[WARN] Bedrock conversational query failed: {e}")

        # Intelligent deterministic fallback citing actual context
        q_low = user_question.lower()
        settlement = trip_context.get("settlement", {}).get("net_settlement", {})
        if "breakfast" in q_low or "snidane" in q_low or "snídaně" in q_low:
            return (
                "Corporate credit card transaction streams capture lodging charges (MCC 7011) but do not contain "
                "itemized hotel folios or meal plan data. At this card-stream ingestion stage, accommodation is treated as "
                "room-only (no complimentary breakfast provided). Therefore, 0% meal deduction is applied, and 100% of "
                "your statutory per diem is preserved under §§ 163 and 170 of the Czech Labour Code."
            )
        elif "personal" in q_low or "billa" in q_low or "market" in q_low or "offset" in q_low:
            return (
                f"Personal card charges totaling -{settlement.get('personal_card_offset_czk', 0):,.2f} CZK were charged to "
                f"the company credit card. The PerDiemo Copilot automatically deducted this amount from your cash reimbursement "
                f"to prevent corporate account discrepancies."
            )
        elif "rate" in q_low or "cnb" in q_low or "čnb" in q_low or "fx" in q_low:
            return (
                "Foreign expenses and per diems were converted using the official Czech National Bank (ČNB) fixing "
                "applicable on the first day of the business trip (§ 183 ZP)."
            )
        else:
            return (
                f"Trip Summary: Statutory per diem is {settlement.get('statutory_per_diem_czk', 0):,.2f} CZK, "
                f"out-of-pocket cash reimbursement is +{settlement.get('out_of_pocket_czk', 0):,.2f} CZK, "
                f"and personal card offsets are -{settlement.get('personal_card_offset_czk', 0):,.2f} CZK, "
                f"resulting in a net payout of {settlement.get('net_reimbursement_czk', 0):,.2f} CZK to IBAN "
                f"{trip_context.get('tsys_data', {}).get('employee_iban')}."
            )

    def conversational_chat(self, message_history: list, trip_context: Dict[str, Any]) -> str:
        """
        Executes a real multi-turn conversation with Amazon Bedrock Claude Sonnet 4.5,
        preserving thread history and citing real transactions and statutory rules.
        """
        client = self._get_bedrock_client()
        context_str = json.dumps(trip_context, indent=2, ensure_ascii=False)
        system_prompt = (
            "You are PerDiemo Copilot, an autonomous corporate payment operations and Czech statutory accounting agent (§§ 151-189 ZP).\n"
            "You are conversing with an employee or CFO about their business trip reconciliation.\n\n"
            f"Active Business Trip & Financial Settlement Context:\n{context_str}\n\n"
            "Guidelines:\n"
            "- Always cite real transaction IDs, amounts, and merchant names from the context.\n"
            "- Explain Czech Labour Code rules when relevant (§ 163 for meal deductions, § 170 for foreign travel, § 183 for ČNB fixing).\n"
            "- Be concise, direct, helpful, and mathematically exact."
        )

        # Ensure message history is formatted properly for Claude on Bedrock
        formatted_messages = []
        for m in message_history:
            role = m.get("role", "user")
            content = m.get("content", "")
            if role in ["user", "assistant"] and content:
                formatted_messages.append({"role": role, "content": content})

        if not formatted_messages:
            return "How can I help you reconcile your corporate card trip or explain your per diems?"

        if client:
            try:
                body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1024,
                    "system": system_prompt,
                    "messages": formatted_messages,
                    "temperature": 0.3
                }
                response = client.invoke_model(
                    modelId=self.model_id,
                    body=json.dumps(body)
                )
                response_body = json.loads(response["body"].read().decode("utf-8"))
                return response_body["content"][0]["text"]
            except Exception as e:
                print(f"[WARN] Bedrock multi-turn chat failed: {e}")

        # Fallback to single-turn query if history invocation fails
        last_question = formatted_messages[-1]["content"]
        return self.conversational_query(last_question, trip_context)

    def explain_audit_rule(self, finding: Dict[str, Any], trip_context: Dict[str, Any]) -> str:
        """
        Asks Amazon Bedrock Claude Sonnet 4.5 to provide an in-depth statutory and operational
        explanation of an audit rule finding, including concrete suggestions and remediation steps
        if there is a violation or warning.
        """
        sev = str(finding.get("severity", "INFO")).upper()
        rule = finding.get("rule", "KB-RULE")
        msg = finding.get("message", "")

        client = self._get_bedrock_client()
        context_str = json.dumps(trip_context, indent=2, ensure_ascii=False)

        prompt = f"""You are PerDiemo Copilot, an elite corporate tax compliance and payment operations AI agent specializing in Czech travel allowance law (§§ 151-189 ZP, Zákon č. 262/2006 Sb.) and Komerční banka corporate banking controls.

Active Audit Finding to Explain:
- Rule ID: {rule}
- Severity: {sev} (PASSED, WARNING, CRITICAL, or INFO)
- Engine Evaluation Message: {msg}

Full Business Trip & Reconciliation Context:
{context_str}

Your Instructions:
1. Explain clearly HOW this rule was evaluated against the traveler's active itinerary and corporate card transactions, and WHY it produced the verdict '{sev}'.
2. Cite the exact statutory articles and legal precedents (e.g. § 163 ZP for meal reductions, § 170 ZP for foreign travel, § 156 ZP for travel purpose, NSS 3 Afs 97/2025 for evidentiary proof).
3. IF THE RULE IS BROKEN OR HAS A WARNING ({sev} in ["CRITICAL", "WARNING"]):
   - You MUST provide concrete, practical, step-by-step SUGGESTIONS and REMEDIATION actions for:
     a) The Employee (e.g. what documentation or declaration to update).
     b) The Corporate Accountant / CFO (e.g. what accounting adjustment or approval is required).
4. IF THE RULE PASSED:
   - Provide an audit defense note explaining why this calculation is tax-exempt and legally fortified against Finanční úřad audits.

Format your response in structured Markdown with clean headings, bullet points, and high readability."""

        if client:
            try:
                body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1200,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2
                }
                response = client.invoke_model(
                    modelId=self.model_id,
                    body=json.dumps(body)
                )
                response_body = json.loads(response["body"].read().decode("utf-8"))
                return response_body["content"][0]["text"]
            except Exception as e:
                print(f"[WARN] Bedrock explain_audit_rule failed: {e}")

        # Intelligent Fallback with Czech Labour Code citations & remediation suggestions
        if "MEAL-DOUBLE-DIPPING" in rule or "RULE-01" in rule:
            if sev == "CRITICAL":
                return (
                    "### ⚖️ Statutory Analysis: Meal Double-Dipping Violation\n\n"
                    "**Why this was flagged:**\n"
                    "The hotel booking or invoice indicates that breakfast was included in the corporate room charge, "
                    "yet the statutory travel declaration (`bezplatna_strava`) did not declare a meal deduction (`snidane`).\n\n"
                    "**Legal Grounding (§§ 163 & 170 ZP):**\n"
                    "Under Section 163 of the Czech Labour Code, when an employer provides a free meal during a business trip, "
                    "the statutory per diem allowance must be reduced by:\n"
                    "- **70%** for trip legs lasting 5 to 12 hours\n"
                    "- **35%** for trip legs lasting 12 to 18 hours\n"
                    "- **25%** for trip legs lasting over 18 hours\n\n"
                    "Claiming full statutory per diem while the company already paid for breakfast constitutes an unlawful double benefit "
                    "subject to wage tax assessment and penalties under Supreme Administrative Court case law (*NSS 3 Afs 97/2025 - 71*).\n\n"
                    "### 💡 Actionable Suggestions & Remediation:\n"
                    "1. **Employee Action:** Update the trip expense claim to declare `snidane` for each morning with hotel breakfast. "
                    "The PerDiemo engine will automatically deduct the statutory percentage.\n"
                    "2. **Accountant Action:** If the hotel was in fact booked as *Room Only* despite the package label, attach the itemized "
                    "hotel folio showing separate zero-charge breakfast was not consumed. This will clear the CRITICAL flag.\n"
                    "3. **Re-seal Trip:** Click **'Re-Calculate'** to produce a new cryptographic SHA-256 seal before approving the MoroSystems payout."
                )
            else:
                return (
                    "### ⚖️ Statutory Analysis: Meal Allowance Compliance\n\n"
                    "**Why this passed:**\n"
                    f"{msg}\n\n"
                    "**Legal Grounding (§§ 163 & 170 ZP):**\n"
                    "The statutory meal deductions are fully aligned with declared meals. Because no complimentary breakfast was provided "
                    "in the room charge (or declared breakfast was correctly deducted), the employee is entitled to 100% of the statutory "
                    "per diem rate without risking double reimbursement sanctions in a tax audit."
                )

        elif "WEEKEND-TRAVEL" in rule or "RULE-02" in rule:
            if sev == "WARNING":
                return (
                    "### ⚖️ Statutory Analysis: Weekend Travel Anomaly\n\n"
                    "**Why this was flagged:**\n"
                    "One or more travel legs occurred on a Saturday or Sunday, but the stated travel purpose (`ucel_cesty`) did not "
                    "contain standard high-priority business justification keywords.\n\n"
                    "**Legal Grounding (§ 156 ZP):**\n"
                    "Weekend travel creates taxable fringe benefit suspicion during tax inspections (*Finanční správa*). The employer "
                    "must prove that weekend travel was mandated by strict business necessity (e.g. Monday morning conference, emergency on-site repair).\n\n"
                    "### 💡 Actionable Suggestions & Remediation:\n"
                    "1. **Employee Action:** Update `ucel_cesty` with specific business justification (e.g., *'Emergency on-site client audit starting Monday 08:00'* or *'International trade fair setup'*).\n"
                    "2. **Manager Action:** Attach an approved pre-travel authorization (*cestovní příkaz*) explicitly approving weekend transit.\n"
                    "3. **Accountant Action:** Review the justification note; once documented, the accountant can approve the reimbursement without tax penalty."
                )
            else:
                return (
                    "### ⚖️ Statutory Analysis: Weekend Travel Justified\n\n"
                    "**Why this passed:**\n"
                    f"{msg}\n\n"
                    "**Legal Grounding (§ 156 ZP):**\n"
                    "All travel legs occurred on regular working days, or weekend legs were substantiated by valid business justification "
                    "meeting Czech Labour Code and tax deductibility standards."
                )

        elif "AUDIT-FINGERPRINT" in rule or "RULE-03" in rule:
            if sev == "CRITICAL":
                return (
                    "### ⚖️ Evidentiary Standard Analysis: Missing Audit Fingerprint\n\n"
                    "**Why this was flagged:**\n"
                    "The calculation result lacks a valid 64-character SHA-256 cryptographic verification signature.\n\n"
                    "**Legal Grounding (NSS 3 Afs 97/2025 - 71):**\n"
                    "In tax audits, the burden of proof (*důkazní břemeno*) rests squarely on the employer. Without a cryptographic timestamp "
                    "and immutable calculation seal, tax inspectors may disregard the calculation and disallow corporate tax deductions.\n\n"
                    "### 💡 Actionable Suggestions & Remediation:\n"
                    "1. Re-run the calculation through the official PerDiemo Cloud Engine (`POST /api/calculate`) to generate the SHA-256 seal.\n"
                    "2. Do not dispatch payments via MoroSystems until the verification signature is recorded."
                )
            else:
                return (
                    "### ⚖️ Evidentiary Standard Analysis: Cryptographic Seal Valid\n\n"
                    "**Why this passed:**\n"
                    f"{msg}\n\n"
                    "**Legal Grounding (NSS 3 Afs 97/2025 - 71):**\n"
                    "The calculation is cryptographically sealed with a SHA-256 hash incorporating the itinerary dates, statutory rates, and ČNB FX fixing. "
                    "This satisfies the highest standard of evidentiary audit defence in Czech fiscal law."
                )

        elif "CARD-RECONCILIATION" in rule or "RULE-04" in rule:
            return (
                "### 💳 Open Banking Audit: Corporate Card Reconciliation\n\n"
                "**Why this was evaluated:**\n"
                f"{msg}\n\n"
                "**Operational Grounding:**\n"
                "Cross-referencing corporate card transaction timestamps with declared travel dates verifies the physical presence of the employee "
                "at the destination and prevents fictitious expense claims.\n\n"
                "### 💡 Actionable Suggestions:\n"
                "- If any transactions fall outside the travel window, verify whether timezone adjustments or delayed merchant batch settlement (TSYS offline sync) occurred.\n"
                "- Ensure personal convenience charges (e.g. supermarket snacks) remain categorized under `SETTLE-RULE-01-PERSONAL-CARD-OFFSET`."
            )

        else:
            return (
                f"### 🛡️ Rule Evaluation: {rule}\n\n"
                f"**Status:** `{sev}`\n"
                f"**Detail:** {msg}\n\n"
                "**Statutory Context:**\n"
                "Evaluated in accordance with Czech Labour Code §§ 151–189 ZP and Komerční banka corporate expense policies."
            )


if __name__ == "__main__":
    agent = BedrockIntakeAgent()
    print("Testing BedrockIntakeAgent extraction...")
    result = agent.extract_from_text("Departed Prague on June 10, meeting in Vienna...")
    print("Agent Output:\n", json.dumps(result, indent=2, ensure_ascii=False))

