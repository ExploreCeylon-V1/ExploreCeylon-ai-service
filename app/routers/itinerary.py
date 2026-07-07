from fastapi import APIRouter, HTTPException
from app.models.request_models import (
    NarrativeRequest,
    RegenerateDayRequest
)
from app.services.openai_service import generate_completion
from app.services.prompt_builder import build_narrative_prompt
from app.services.prompt_builder import build_regenerate_day_prompt

router = APIRouter(prefix="/ai", tags=["Itinerary"])


@router.post("/itinerary/narrate")
async def narrate_itinerary(request: NarrativeRequest):
    """The backend (TripService + ItineraryAssemblyService) has already
    decided the full day/stop structure — this endpoint only asks the
    LLM to write narrative text (title, per-day theme/tips, per-stop
    description) for that fixed structure. It replaces the old
    /ai/itinerary/generate, which used to let the LLM plan the whole
    trip's geography/day-grouping itself."""
    try:
        prompt = build_narrative_prompt(request)
        result = await generate_completion(prompt, max_tokens=4000)
        return {"success": True, "data": result}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Narrative generation failed: {str(e)}"
        )


@router.post("/itinerary/regenerate-day")
async def regenerate_day(request: RegenerateDayRequest):
    try:
        prompt = build_regenerate_day_prompt(
            day_number      = request.day_number,
            current_region  = request.current_region,
            travel_style    = request.travel_style,
            budget_range    = request.budget_range,
            exclude_regions = request.exclude_regions
        )

        result = await generate_completion(
            prompt, max_tokens=1000)
        return {"success": True, "data": result}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Day regeneration failed: {str(e)}"
        )