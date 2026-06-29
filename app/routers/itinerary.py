from fastapi import APIRouter, HTTPException
from app.models.request_models import (
    ItineraryRequest,
    RegenerateDayRequest
)
from app.services.openai_service import generate_completion
from app.services.prompt_builder import build_itinerary_prompt
from app.services.prompt_builder import build_regenerate_day_prompt

router = APIRouter(prefix="/ai", tags=["Itinerary"])


@router.post("/itinerary/generate")
async def generate_itinerary(request: ItineraryRequest):
    try:
        # ← await added (now async)
        prompt = await build_itinerary_prompt(
            start_date     = request.start_date,
            end_date       = request.end_date,
            travel_style   = request.travel_style,
            budget_range   = request.budget_range,
            group_size     = request.group_size,
            regions        = request.regions,
            interests      = request.interests,
            starting_point = request.starting_point,
            special_notes  = request.special_notes,
            from_location  = request.from_location,  
            to_location    = request.to_location
        )

        result = await generate_completion(
            prompt, max_tokens=4000)
        return {"success": True, "data": result}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Itinerary generation failed: {str(e)}"
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