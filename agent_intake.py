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
import io
from typing import Dict, Any, Optional, List, Union
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from pypdf import PdfReader
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False

try:
    from pdf2image import convert_from_bytes
    HAS_PDF2IMAGE = True
except ImportError:
    HAS_PDF2IMAGE = False

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

AWS_REGION = os.environ.get("AWS_REGION", "eu-central-1")
# In Europe, Claude runs through EU cross-region inference profiles, so model ID needs 'eu.' prefix:
# Sonnet 4.5: eu.anthropic.claude-sonnet-4-5-20250929-v1:0 (recommended for extraction accuracy)
# Haiku 4.5:  eu.anthropic.claude-haiku-4-5-20251001-v1:0 (recommended for high-volume drafting)
BEDROCK_MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "eu.anthropic.claude-sonnet-4-5-20250929-v1:0")

EXTRACTION_SYSTEM_PROMPT = """You are an expert corporate travel auditor and multimodal parser for Czech statutory per diem accounting.
Your task is to analyze travel documents (flight boarding passes, train bookings, hotel folios, taxi receipts, meal receipts) or text logs, and extract a structured travel itinerary complying with statutory accounting rules.

Return a strictly valid JSON object matching this schema:
{
  "document_type": "hotel_folio | boarding_pass | meal_receipt | taxi_receipt | train_ticket | other",
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
  },
  "meal_receipt": {
    "meal_type": "breakfast | lunch | dinner | null",
    "date": "YYYY-MM-DD or null",
    "amount": 0.0,
    "currency": "EUR | CZK | etc"
  }
}

IMPORTANT: If this is a meal receipt (restaurant, cafe, etc.), set document_type to "meal_receipt" and fill in the meal_receipt object.
Classify meal_type based on content: breakfast items (eggs, coffee, croissant, Frühstück), lunch, or dinner.

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
        if self._client is None:
            try:
                import boto3
                profile = os.environ.get("AWS_PROFILE")
                if profile:
                    session = boto3.Session(profile_name=profile)
                    self._client = session.client(
                        service_name="bedrock-runtime",
                        region_name=self.region_name
                    )
                else:
                    self._client = boto3.client(
                        service_name="bedrock-runtime",
                        region_name=self.region_name
                    )
            except Exception as e:
                print(f"[WARN] Failed to initialize AWS Bedrock client: {e}. Falling back to mock generator.")
                self._client = None
        return self._client

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
            "max_tokens": 4096,
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

    def extract_from_pdf(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """Extract from PDF by converting pages to images and processing with vision."""
        # Try pdf2image first (converts PDF to images for vision processing)
        if HAS_PDF2IMAGE:
            try:
                images = convert_from_bytes(pdf_bytes, dpi=200, first_page=1, last_page=5)
                all_extractions = []

                for img in images:
                    img_byte_arr = io.BytesIO()
                    img.save(img_byte_arr, format='PNG')
                    img_bytes = img_byte_arr.getvalue()

                    extraction = self.extract_from_image(img_bytes, mime_type="image/png")
                    if extraction and extraction.get("itinerary"):
                        all_extractions.append(extraction)

                if all_extractions:
                    return self._merge_extractions(all_extractions)

            except Exception as e:
                print(f"[WARN] pdf2image extraction failed: {e}. Trying text fallback.")

        # Fallback to text extraction
        return self._extract_pdf_text_fallback(pdf_bytes)

    def _extract_pdf_text_fallback(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """Fallback: extract text from PDF and process as text."""
        if HAS_PYPDF:
            try:
                reader = PdfReader(io.BytesIO(pdf_bytes))
                text = ""
                for page in reader.pages[:5]:  # Limit to first 5 pages
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                if text.strip():
                    return self.extract_from_text(text)
            except Exception as e:
                print(f"[WARN] pypdf text extraction failed: {e}")
        return self._mock_extraction("PDF document")

    def extract_from_file(self, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        """Auto-detect file type and extract accordingly."""
        filename_lower = filename.lower()

        if filename_lower.endswith(".pdf"):
            return self.extract_from_pdf(file_bytes)
        elif filename_lower.endswith((".png", ".jpg", ".jpeg", ".webp", ".gif")):
            mime_map = {
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".webp": "image/webp",
                ".gif": "image/gif"
            }
            ext = "." + filename_lower.rsplit(".", 1)[-1]
            mime_type = mime_map.get(ext, "image/jpeg")
            return self.extract_from_image(file_bytes, mime_type)
        elif filename_lower.endswith((".txt", ".md")):
            text = file_bytes.decode("utf-8", errors="ignore")
            return self.extract_from_text(text)
        else:
            # Try as image first, then text
            try:
                return self.extract_from_image(file_bytes, "image/jpeg")
            except:
                text = file_bytes.decode("utf-8", errors="ignore")
                return self.extract_from_text(text)

    def _merge_extractions(self, extractions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge multiple page extractions into a single result."""
        if not extractions:
            return self._mock_extraction("merged document")

        merged = extractions[0].copy()

        for ext in extractions[1:]:
            # Merge itineraries
            if ext.get("itinerary"):
                merged.setdefault("itinerary", []).extend(ext["itinerary"])

            # Merge free meals
            if ext.get("bezplatna_strava"):
                merged.setdefault("bezplatna_strava", {}).update(ext["bezplatna_strava"])

            # Take hotel info if not present
            if ext.get("hotel_info") and not merged.get("hotel_info", {}).get("hotel_name"):
                merged["hotel_info"] = ext["hotel_info"]

            # Take purpose if not present
            if ext.get("ucel_cesty") and not merged.get("ucel_cesty"):
                merged["ucel_cesty"] = ext["ucel_cesty"]

        # Sort itinerary by date
        if merged.get("itinerary"):
            merged["itinerary"] = sorted(
                merged["itinerary"],
                key=lambda x: x.get("datum", "")
            )

        return merged

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

if __name__ == "__main__":
    agent = BedrockIntakeAgent()
    print("Testing BedrockIntakeAgent extraction...")
    result = agent.extract_from_text("Departed Prague on June 10, meeting in Vienna...")
    print("Agent Output:\n", json.dumps(result, indent=2, ensure_ascii=False))
