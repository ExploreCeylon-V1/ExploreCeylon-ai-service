def test_monsoon_check_returns_warning_for_sw_monsoon(client):
    payload = {
        "regions": ["Colombo", "Galle"],
        "start_date": "2026-06-01",
        "end_date": "2026-07-15",
    }

    response = client.post("/ai/monsoon-check", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True

    data = body["data"]
    assert "warnings" in data
    assert "has_warning" in data
    assert data["has_warning"] is True
    assert len(data["warnings"]) > 0

    warning = data["warnings"][0]
    assert warning["type"] == "SW_MONSOON"
    assert "Colombo" in warning["affected_regions"] or "Galle" in warning["affected_regions"]
    assert "description" in warning
    assert "recommendation" in warning


def test_monsoon_check_no_warning_for_safe_region_and_dry_months(client):
    payload = {
        "regions": ["Arugam Bay"],
        "start_date": "2026-02-01",
        "end_date": "2026-02-01",
    }

    response = client.post("/ai/monsoon-check", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["has_warning"] is False
    assert body["data"]["warnings"] == []
