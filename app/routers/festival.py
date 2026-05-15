from fastapi import APIRouter
from app.models.request_models import FestivalRequest
from app.data.festivals_data import get_festivals_for_dates

router = APIRouter(prefix="/ai", tags=["Festivals"])


@router.post("/festival-suggestions")
async def get_festival_suggestions(request: FestivalRequest):
    festivals = get_festivals_for_dates(
        start_month = request.start_date.month,
        end_month   = request.end_date.month,
        regions     = request.regions
    )
    return {
        "success": True,
        "data": {
            "festivals": festivals,
            "count": len(festivals)
        }
    }