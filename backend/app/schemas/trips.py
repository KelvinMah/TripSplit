from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TravelerInput(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    interests: list[str] = Field(default_factory=list, max_length=20)
    avoid: list[str] = Field(default_factory=list, max_length=20)
    max_daily_budget: int | None = Field(default=None, ge=0)
    notes: str = Field(default="", max_length=2000)


class TravelerView(TravelerInput):
    id: str
    model_config = ConfigDict(from_attributes=True)


class TripCreate(BaseModel):
    title: str = Field(min_length=2, max_length=120)
    destination: str = Field(min_length=2, max_length=120)
    days: int = Field(ge=1, le=14)
    budget_per_person: int = Field(ge=0, le=100000)


class StopView(BaseModel):
    id: str
    day: int
    position: int
    name: str
    category: str
    estimated_cost: int
    rationale: str
    place_id: str | None
    model_config = ConfigDict(from_attributes=True)


class TripView(TripCreate):
    id: str
    created_at: datetime
    travelers: list[TravelerView]
    itinerary: list[StopView]
    model_config = ConfigDict(from_attributes=True)


class ConversationInput(BaseModel):
    conversation: str = Field(min_length=5, max_length=15000)


class PreferenceExtraction(BaseModel):
    travelers: list[TravelerInput]
    destinations: list[str]
    shared_interests: list[str]
    warnings: list[str]
    source: str


class Conflict(BaseModel):
    type: str
    travelers: list[str]
    detail: str


class GenerateResult(BaseModel):
    itinerary: list[StopView]
    conflicts: list[Conflict]
    notes: list[str]
