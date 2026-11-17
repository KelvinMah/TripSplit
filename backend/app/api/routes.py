import httpx

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.database import get_db
from app.models.entities import Traveler, Trip
from app.schemas.trips import (ConversationInput, GenerateResult, PreferenceExtraction,
                               TravelerInput, TravelerView, TripCreate, TripView)
from app.services.maps import search_places
from app.services.planning import build_itinerary, detect_conflicts
from app.services.preferences import extract_preferences

router = APIRouter(prefix="/api")


def get_trip(db: Session, trip_id: str) -> Trip:
    trip = db.scalar(select(Trip).options(selectinload(Trip.travelers),
                                          selectinload(Trip.itinerary)).where(Trip.id == trip_id))
    if trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.post("/trips", response_model=TripView, status_code=201)
def create_trip(payload: TripCreate, db: Session = Depends(get_db)) -> Trip:
    trip = Trip(**payload.model_dump())
    db.add(trip)
    db.commit()
    return get_trip(db, trip.id)


@router.get("/trips", response_model=list[TripView])
def list_trips(db: Session = Depends(get_db)) -> list[Trip]:
    return list(db.scalars(select(Trip).options(selectinload(Trip.travelers),
                                               selectinload(Trip.itinerary)).order_by(Trip.created_at.desc())))


@router.get("/trips/{trip_id}", response_model=TripView)
def read_trip(trip_id: str, db: Session = Depends(get_db)) -> Trip:
    return get_trip(db, trip_id)


@router.delete("/trips/{trip_id}", status_code=204)
def delete_trip(trip_id: str, db: Session = Depends(get_db)) -> None:
    db.delete(get_trip(db, trip_id))
    db.commit()


@router.post("/trips/{trip_id}/travelers", response_model=TravelerView, status_code=201)
def add_traveler(trip_id: str, payload: TravelerInput, db: Session = Depends(get_db)) -> Traveler:
    get_trip(db, trip_id)
    traveler = Traveler(trip_id=trip_id, **payload.model_dump())
    db.add(traveler)
    db.commit()
    db.refresh(traveler)
    return traveler


@router.delete("/trips/{trip_id}/travelers/{traveler_id}", status_code=204)
def delete_traveler(trip_id: str, traveler_id: str, db: Session = Depends(get_db)) -> None:
    get_trip(db, trip_id)
    traveler = db.get(Traveler, traveler_id)
    if traveler is None or traveler.trip_id != trip_id:
        raise HTTPException(status_code=404, detail="Traveler not found")
    db.delete(traveler)
    db.commit()


@router.post("/preferences/extract", response_model=PreferenceExtraction)
def extract(payload: ConversationInput) -> PreferenceExtraction:
    try:
        return extract_preferences(payload.conversation)
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Preference extraction service unavailable") from exc


@router.post("/trips/{trip_id}/generate", response_model=GenerateResult)
def generate(trip_id: str, db: Session = Depends(get_db)) -> GenerateResult:
    trip = get_trip(db, trip_id)
    conflicts = detect_conflicts(trip)
    stops, notes = build_itinerary(trip)
    trip.itinerary.clear()
    db.flush()
    trip.itinerary.extend(stops)
    db.commit()
    trip = get_trip(db, trip_id)
    return GenerateResult(itinerary=trip.itinerary, conflicts=conflicts, notes=notes)


@router.get("/places/search")
async def places_search(query: str = Query(min_length=2, max_length=100),
                        destination: str = Query(min_length=2, max_length=100)) -> dict:
    try:
        return await search_places(query, destination)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Places service unavailable") from exc
