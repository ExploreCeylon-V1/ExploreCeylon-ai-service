from fastapi import APIRouter
from app.models.request_models import MonsoonCheckRequest
from app.data.monsoon_data import get_monsoon_warning

router = APIRouter(prefix="/ai", tags=["Monsoon"])


@router.post("/monsoon-check")
async def check_monsoon(request: MonsoonCheckRequest):
    months = list(range(
        request.start_date.month,
        request.end_date.month + 1
    ))
    result = get_monsoon_warning(request.regions, months)
    return {"success": True, "data": result}