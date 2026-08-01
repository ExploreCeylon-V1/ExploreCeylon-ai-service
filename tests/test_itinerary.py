from unittest.mock import AsyncMock, patch


def test_narrate_itinerary_returns_mocked_narrative(client):
    payload = {
        "start_date": "2026-08-01",
        "end_date": "2026-08-02",
        "travel_style": "CULTURAL",
        "budget_range": "MID_RANGE",
        "group_size": 2,
        "starting_point": "Colombo",
        "to_location": "Kandy",
        "special_notes": "Vegetarian meals preferred",
        "days": [
            {
                "dayNumber": 1,
                "date": "2026-08-01",
                "region": "Colombo",
                "stops": [
                    {"type": "DESTINATION", "name": "Galle Face Green", "slot": "MORNING"},
                    {"type": "GEM", "name": "Hidden Spice Garden", "slot": "AFTERNOON"},
                ],
            },
            {
                "dayNumber": 2,
                "date": "2026-08-02",
                "region": "Kandy",
                "stops": [
                    {"type": "DESTINATION", "name": "Temple of the Tooth", "slot": "MORNING"},
                ],
            },
        ],
    }

    fake_llm_response = {
        "tripTitle": "A Cultural Journey Through Sri Lanka",
        "days": [
            {
                "dayNumber": 1,
                "theme": "Coastal Colombo Charm",
                "tips": "Wear light clothing and bring sunscreen.",
                "stops": [
                    {"description": "Stroll along the scenic oceanfront promenade."},
                    {"description": "Discover fragrant spices at this tucked-away garden."},
                ],
            },
            {
                "dayNumber": 2,
                "theme": "Sacred Kandy",
                "tips": "Dress modestly and remove shoes before entering.",
                "stops": [
                    {"description": "Visit the revered relic of the Buddha's tooth."},
                ],
            },
        ],
    }

    with patch(
        "app.routers.itinerary.generate_completion",
        new_callable=AsyncMock,
        return_value=fake_llm_response,
    ) as mocked_generate_completion:
        response = client.post("/ai/itinerary/narrate", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body == {"success": True, "data": fake_llm_response}

    mocked_generate_completion.assert_awaited_once()
    call_args = mocked_generate_completion.call_args
    assert call_args.kwargs.get("max_tokens") == 4000
    prompt_arg = call_args.args[0]
    assert "Galle Face Green" in prompt_arg
    assert "Temple of the Tooth" in prompt_arg


def test_regenerate_day_returns_mocked_day(client):
    payload = {
        "trip_id": 42,
        "day_number": 3,
        "current_region": "Kandy",
        "exclude_regions": ["Colombo"],
        "travel_style": "ADVENTURE",
        "budget_range": "LUXURY",
    }

    fake_llm_response = {
        "dayNumber": 3,
        "region": "Kandy",
        "theme": "Highland Adventure",
        "locations": ["Knuckles Range", "Riverston", "Corbett's Gap"],
        "meals": ["breakfast", "lunch", "dinner"],
        "hiddenGem": "Riverston viewpoint",
        "festivalEvent": None,
        "tips": "Bring hiking boots and rain gear.",
        "estimatedDayCost": 85,
    }

    with patch(
        "app.routers.itinerary.generate_completion",
        new_callable=AsyncMock,
        return_value=fake_llm_response,
    ) as mocked_generate_completion:
        response = client.post("/ai/itinerary/regenerate-day", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body == {"success": True, "data": fake_llm_response}

    mocked_generate_completion.assert_awaited_once()
    call_args = mocked_generate_completion.call_args
    assert call_args.kwargs.get("max_tokens") == 1000
    prompt_arg = call_args.args[0]
    assert "Kandy" in prompt_arg


def test_narrate_itinerary_handles_llm_failure(client):
    payload = {
        "start_date": "2026-08-01",
        "end_date": "2026-08-01",
        "travel_style": "CULTURAL",
        "budget_range": "MID_RANGE",
        "group_size": 2,
        "starting_point": "Colombo",
        "days": [
            {
                "dayNumber": 1,
                "date": "2026-08-01",
                "region": "Colombo",
                "stops": [
                    {"type": "DESTINATION", "name": "Galle Face Green", "slot": "MORNING"},
                ],
            },
        ],
    }

    with patch(
        "app.routers.itinerary.generate_completion",
        new_callable=AsyncMock,
        side_effect=RuntimeError("Groq API error: boom"),
    ):
        response = client.post("/ai/itinerary/narrate", json=payload)

    assert response.status_code == 500
    assert "Narrative generation failed" in response.json()["detail"]
