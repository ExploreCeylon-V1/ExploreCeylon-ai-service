def test_festival_suggestions_returns_island_wide_new_year(client):
    payload = {
        "start_date": "2026-04-01",
        "end_date": "2026-04-30",
        "regions": ["Colombo"],
    }

    response = client.post("/ai/festival-suggestions", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True

    data = body["data"]
    assert "festivals" in data
    assert "count" in data
    assert data["count"] == len(data["festivals"])
    assert data["count"] > 0

    names = [f["name"] for f in data["festivals"]]
    assert "Sinhala and Tamil New Year" in names


def test_festival_suggestions_no_match_for_quiet_month(client):
    payload = {
        "start_date": "2026-02-01",
        "end_date": "2026-02-28",
        "regions": ["Nowhere Region"],
    }

    response = client.post("/ai/festival-suggestions", json=payload)

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["count"] == 0
    assert data["festivals"] == []
