from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def new_id() -> str:
    return str(uuid4())


class Trip(Base):
    __tablename__ = "trips"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    title: Mapped[str] = mapped_column(String(120))
    destination: Mapped[str] = mapped_column(String(120))
    days: Mapped[int] = mapped_column(Integer)
    budget_per_person: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    travelers: Mapped[list["Traveler"]] = relationship(back_populates="trip", cascade="all, delete-orphan")
    itinerary: Mapped[list["ItineraryStop"]] = relationship(back_populates="trip", cascade="all, delete-orphan")


class Traveler(Base):
    __tablename__ = "travelers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    trip_id: Mapped[str] = mapped_column(ForeignKey("trips.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(80))
    interests: Mapped[list] = mapped_column(JSON, default=list)
    avoid: Mapped[list] = mapped_column(JSON, default=list)
    max_daily_budget: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str] = mapped_column(Text, default="")
    trip: Mapped[Trip] = relationship(back_populates="travelers")


class ItineraryStop(Base):
    __tablename__ = "itinerary_stops"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    trip_id: Mapped[str] = mapped_column(ForeignKey("trips.id", ondelete="CASCADE"))
    day: Mapped[int] = mapped_column(Integer)
    position: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(160))
    category: Mapped[str] = mapped_column(String(60))
    estimated_cost: Mapped[int] = mapped_column(Integer, default=0)
    rationale: Mapped[str] = mapped_column(Text, default="")
    place_id: Mapped[str | None] = mapped_column(String(200), nullable=True)
    trip: Mapped[Trip] = relationship(back_populates="itinerary")
