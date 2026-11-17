def create_trip(client):
    response = client.post("/api/trips", json={
        "title": "Weekend getaway", "destination": "Vancouver",
        "days": 2, "budget_per_person": 60,
    })
    assert response.status_code == 201
    return response.json()["id"]


def test_trip_crud(client):
    trip_id = create_trip(client)
    assert client.get(f"/api/trips/{trip_id}").status_code == 200
    assert len(client.get("/api/trips").json()) == 1
    assert client.delete(f"/api/trips/{trip_id}").status_code == 204
    assert client.get(f"/api/trips/{trip_id}").status_code == 404


def test_conflicts_and_budget(client):
    trip_id = create_trip(client)
    for traveler in [
        {"name": "Alex", "interests": ["hiking", "food"], "max_daily_budget": 20},
        {"name": "Sam", "interests": ["art"], "avoid": ["hiking"]},
    ]:
        assert client.post(f"/api/trips/{trip_id}/travelers", json=traveler).status_code == 201
    result = client.post(f"/api/trips/{trip_id}/generate").json()
    assert {item["type"] for item in result["conflicts"]} == {"budget", "interest"}
    assert all(stop["estimated_cost"] <= 20 for stop in result["itinerary"])
    assert all(stop["category"] != "hiking" for stop in result["itinerary"])
    assert len(result["itinerary"]) <= 6


def test_extract_without_key(client):
    response = client.post("/api/preferences/extract", json={
        "conversation": "Alex: I love hiking and food, budget $40\nSam: I avoid hiking, love art"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "heuristic"
    assert len(data["travelers"]) == 2


def test_input_validation(client):
    assert client.post("/api/trips", json={"title": "X", "destination": "Y", "days": 0,
                                            "budget_per_person": -1}).status_code == 422
