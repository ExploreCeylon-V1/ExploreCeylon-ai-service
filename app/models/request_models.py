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
    travel_style: str = "MID_RANGE"
    group_size: int = 2
    regions: List[str] = []

class FestivalRequest(BaseModel):
    start_date: date
    end_date: date
    regions: List[str] = []