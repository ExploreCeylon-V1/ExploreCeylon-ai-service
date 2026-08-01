def test_budget_estimate_mid_range(client):
    payload = {
        "duration_days": 5,
        "budget_range": "MID_RANGE",
        "group_size": 2,
        "regions": ["Colombo", "Kandy"],
    }

    response = client.post("/ai/budget-estimate", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True

    data = body["data"]
    assert data["budget_range"] == "MID_RANGE"
    assert data["duration_days"] == 5
    assert data["group_size"] == 2
    assert data["currency"] == "USD"

    # MID_RANGE rates: hotel=60, food=25, transport=20, activities=15 => 120/day/person
    assert data["per_person_total"] == 600
    assert data["group_total"] == 1200

    breakdown = data["daily_breakdown"]
    assert breakdown["accommodation"] == 300
    assert breakdown["food"] == 125
    assert breakdown["transport"] == 100
    assert breakdown["activities"] == 75


def test_budget_estimate_unknown_range_defaults_to_mid_range(client):
    payload = {
        "duration_days": 1,
        "budget_range": "NOT_A_REAL_RANGE",
        "group_size": 1,
        "regions": [],
    }

    response = client.post("/ai/budget-estimate", json=payload)

    assert response.status_code == 200
    data = response.json()["data"]
    # Falls back to MID_RANGE rates -> 120/day/person
    assert data["per_person_total"] == 120
