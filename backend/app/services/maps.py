import httpx

from app.core.config import settings


async def search_places(query: str, destination: str) -> dict:
    """Optional Places Text Search. Never treat returned places as verified itinerary stops."""
    if not settings.google_maps_api_key:
        return {"source": "disabled", "places": [], "message": "Set GOOGLE_MAPS_API_KEY to enable Places."}
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(
            "https://places.googleapis.com/v1/places:searchText",
            headers={
                "X-Goog-Api-Key": settings.google_maps_api_key,
                "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.location",
            },
            json={"textQuery": f"{query} in {destination}", "maxResultCount": 8},
        )
        response.raise_for_status()
        return {"source": "google_places", "places": response.json().get("places", [])}
