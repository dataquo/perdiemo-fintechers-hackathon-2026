"""API.md-aligned inputs; NO statutory financial calculations live here."""
from __future__ import annotations

from datetime import datetime
import re
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator

EventType = Literal[
    "ODJEZD", "PRIJEZD", "HRANICE_PRECHOD", "NÁVRAT_ODJEZD",
    "HRANICE_NAVRAT", "KREUZ_NAVRAT",
]
TransportType = Literal[
    "company_car", "private_vehicle", "plane", "train", "bus",
    "public_transit", "walk",
]
MealType = Literal["snidane", "obed", "vecer"]


def _valid_local_datetime(value: str) -> datetime:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}", value):
        raise ValueError("expected YYYY-MM-DDTHH:MM (no timezone offset)")
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M")
    except ValueError as exc:
        raise ValueError("invalid calendar date/time") from exc


class Leg(BaseModel):
    model_config = ConfigDict(extra="forbid")
    typ: EventType
    datum: str
    misto: Annotated[str, Field(min_length=1, max_length=300)]
    country_code: str
    vzdalenost_km: Annotated[float, Field(ge=0, allow_inf_nan=False)] | None = None
    transport_type: TransportType | None = None
    layover_type: str | None = None  # Present in existing API.md examples

    @field_validator("datum")
    @classmethod
    def check_datum(cls, value: str) -> str:
        _valid_local_datetime(value)
        return value

    @field_validator("country_code")
    @classmethod
    def check_country_code(cls, value: str) -> str:
        if not re.fullmatch(r"[A-Z]{3}", value):
            raise ValueError("expected uppercase ISO alpha-3 country code")
        return value


class Trip(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id_cesty: Annotated[str, Field(min_length=1, max_length=150)]
    vlastnictvi_vozidla: Literal["SLUZEBNI", "OSOBNI"]
    itinerar: Annotated[list[Leg], Field(min_length=2)]
    ucel_cesty: str | None = None
    zamestnanec_jednatel: str | None = None
    spolecnost: str | None = None
    bezplatna_strava: dict[str, list[MealType]] = Field(default_factory=dict)

    @field_validator("bezplatna_strava")
    @classmethod
    def check_free_meal_dates(cls, value: dict[str, list[MealType]]) -> dict[str, list[MealType]]:
        for date in value:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
                raise ValueError(f"Invalid date key {date!r}; expected YYYY-MM-DD")
            try:
                datetime.strptime(date, "%Y-%m-%d")
            except ValueError as exc:
                raise ValueError(f"Invalid calendar date {date!r}") from exc
        return value

    @model_validator(mode="after")
    def check_event_order(self) -> "Trip":
        dates = [_valid_local_datetime(leg.datum) for leg in self.itinerar]
        if dates != sorted(dates):
            raise ValueError("itinerar events must be sorted chronologically")
        # Only validate order and shape, not legal itinerary eligibility or
        # free-meal reduction percentages; those belong to PerDiemo.
        return self


class CalculationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    year: Annotated[int, Field(ge=2000, le=2100, strict=True)]
    trips: Annotated[list[Trip], Field(min_length=1)]
    include_routes: bool = True

    @model_validator(mode="after")
    def check_trip_identifiers(self) -> "CalculationRequest":
        ids = [t.id_cesty for t in self.trips]
        if len(ids) != len(set(ids)):
            raise ValueError("trips[].id_cesty must be unique in a calculation request")
        return self


def validate_request(payload: dict[str, Any]) -> dict[str, Any]:
    """Report valid+normalized REST payload or actionable Pydantic errors.

    Input is PerDiemo's NATIVE calculation schema, not a matching-candidate
    wrapper and not the output of /api/parse-itinerary.
    """
    try:
        request = CalculationRequest.model_validate(payload)
    except ValidationError as exc:
        return {
            "ok": False,
            "error": {
                "code": "INVALID_TRIP_INPUT",
                "message": "Trip data does not satisfy the documented PerDiemo calculation schema.",
                "issues": [
                    {"path": ".".join(str(x) for x in item["loc"]),
                     "message": item["msg"], "type": item["type"]}
                    for item in exc.errors(include_url=False)
                ],
            },
        }
    return {"ok": True, "payload": request.model_dump(exclude_none=True)}
