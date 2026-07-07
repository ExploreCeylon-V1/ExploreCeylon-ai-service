from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class ItineraryRequest(BaseModel):
    start_date: date
    end_date: date
    travel_style: str = "CULTURAL"
    budget_range: str = "MID_RANGE"
    group_size: int = 2
    regions: List[str] = []
    interests: List[str] = []
    starting_point: str = "Colombo"
    special_notes: Optional[str] = None
    trip_id: Optional[int] = None
    from_location: Optional[str] = None
    to_location: Optional[str] = None

class PlannedStop(BaseModel):
    """A single stop the backend has already decided on — the LLM only
    fills in a `description` for it (see /ai/itinerary/narrate); it must
    not add, remove or reorder stops."""
    type: str          # DESTINATION | GEM | EVENT
    name: str
    slot: str          # MORNING | AFTERNOON | EVENING


class PlannedDay(BaseModel):
    """A single day's fixed structure, already assembled by the backend's
    ItineraryAssemblyService. The LLM only writes theme/tips for the day
    and a description per stop."""
    dayNumber: int
    date: str
    region: Optional[str] = None
    stops: List[PlannedStop] = []


class NarrativeRequest(BaseModel):
    """Request body for /ai/itinerary/narrate — the corridor, day
    assignment, stop order and referenceId are already final by the time
    this reaches the AI service; it only writes narrative text."""
    start_date: date
    end_date: date
    travel_style: str = "CULTURAL"
    budget_range: str = "MID_RANGE"
    group_size: int = 2
    starting_point: str = "Colombo"
    to_location: Optional[str] = None
    special_notes: Optional[str] = None
    days: List[PlannedDay] = []


class RegenerateDayRequest(BaseModel):
    trip_id: int
    day_number: int
    current_region: str
    exclude_regions: List[str] = []
    travel_style: str = "CULTURAL"
    budget_range: str = "MID_RANGE"

class MonsoonCheckRequest(BaseModel):
    regions: List[str]
    start_date: date
    end_date: date

class BudgetEstimateRequest(BaseModel):
    duration_days: int
    budget_range: str = "MID_RANGE"
    group_size: int = 2
    regions: List[str] = []

class FestivalRequest(BaseModel):
    start_date: date
    end_date: date
    regions: List[str] = []