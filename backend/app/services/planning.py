from collections import Counter

from app.models.entities import ItineraryStop, Trip
from app.schemas.trips import Conflict

CANDIDATES = [
    ("Historic district walk", "history", 0),
    ("Local food market", "food", 25),
    ("Art museum", "art", 20),
    ("Scenic nature trail", "hiking", 0),
    ("Coffee tasting", "coffee", 15),
    ("Waterfront promenade", "beach", 0),
    ("Botanical garden", "nature", 15),
    ("Shopping district", "shopping", 30),
    ("Architecture walking tour", "architecture", 0),
    ("Evening live music", "nightlife", 30),
    ("Photography viewpoint", "photography", 0),
    ("City park picnic", "parks", 12),
    ("Cultural museum", "museum", 18),
]


def detect_conflicts(trip: Trip) -> list[Conflict]:
    conflicts: list[Conflict] = []
    for traveler in trip.travelers:
        if traveler.max_daily_budget is not None and traveler.max_daily_budget < trip.budget_per_person:
            conflicts.append(Conflict(type="budget", travelers=[traveler.name], detail=(
                f"{traveler.name}'s daily limit ({traveler.max_daily_budget}) is below "
                f"the trip target ({trip.budget_per_person})."
            )))
    for traveler in trip.travelers:
        for other in trip.travelers:
            if traveler.id >= other.id:
                continue
            opposed = set(traveler.interests) & set(other.avoid)
            opposed |= set(other.interests) & set(traveler.avoid)
            if opposed:
                conflicts.append(Conflict(type="interest", travelers=[traveler.name, other.name],
                                          detail=f"Conflicting preferences: {', '.join(sorted(opposed))}."))
    return conflicts


def build_itinerary(trip: Trip) -> tuple[list[ItineraryStop], list[str]]:
    """Deterministic budget-aware preference scoring; not a geographic route optimizer."""
    votes = Counter(term.lower() for traveler in trip.travelers for term in traveler.interests)
    avoided = {term.lower() for traveler in trip.travelers for term in traveler.avoid}
    limits = [t.max_daily_budget for t in trip.travelers if t.max_daily_budget is not None]
    daily_budget = min([trip.budget_per_person, *limits]) if limits else trip.budget_per_person
    ranked = sorted(
        [item for item in CANDIDATES if item[1] not in avoided and item[2] <= daily_budget],
        key=lambda item: (-votes[item[1]], item[2], item[0]),
    )
    if not ranked:
        return [], ["No candidate activities fit the group's budget and exclusions."]
    stops: list[ItineraryStop] = []
    for day in range(1, trip.days + 1):
        remaining = daily_budget
        for name, category, cost in ranked[(day - 1) * 3:] + ranked[:(day - 1) * 3]:
            if len([stop for stop in stops if stop.day == day]) >= 3:
                break
            if cost > remaining or (name, day) in {(s.name, s.day) for s in stops}:
                continue
            stops.append(ItineraryStop(trip_id=trip.id, day=day,
                                       position=1 + len([s for s in stops if s.day == day]),
                                       name=name, category=category, estimated_cost=cost,
                                       rationale=f"Matches {votes[category]} traveler preference(s)."))
            remaining -= cost
    return stops, ["Activity suggestions are generic templates, not verified local businesses.",
                   "Route times and opening hours are not calculated; verify before traveling."]
