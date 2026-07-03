from fastapi import APIRouter, HTTPException
from app.models.request_models import BudgetEstimateRequest
from app.services.openai_service import generate_completion

router = APIRouter(prefix="/ai", tags=["Budget"])

BUDGET_RATES = {
    "BUDGET":    {"hotel": 15, "food": 10, "transport": 8,  "activities": 5},
    "MID_RANGE": {"hotel": 60, "food": 25, "transport": 20, "activities": 15},
    "LUXURY":    {"hotel": 200,"food": 60, "transport": 50, "activities": 40},
}

@router.post("/budget-estimate")
async def estimate_budget(request: BudgetEstimateRequest):
    try:
        rates = BUDGET_RATES.get(
            request.budget_range.upper(), BUDGET_RATES["MID_RANGE"])

        per_person_per_day = sum(rates.values())
        total_per_person   = per_person_per_day * request.duration_days
        total_group        = total_per_person * request.group_size

        breakdown = {
            "accommodation": rates["hotel"]      * request.duration_days,
            "food":          rates["food"]       * request.duration_days,
            "transport":     rates["transport"]  * request.duration_days,
            "activities":    rates["activities"] * request.duration_days,
        }

        return {
            "success": True,
            "data": {
                "budget_range":      request.budget_range,
                "duration_days":     request.duration_days,
                "group_size":        request.group_size,
                "per_person_total":  round(total_per_person, 2),
                "group_total":       round(total_group, 2),
                "currency":          "USD",
                "daily_breakdown":   breakdown,
                "note": (
                    "Estimates are approximate. "
                    "Actual costs may vary by season and availability."
                )
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Budget estimation failed: {str(e)}"
        )