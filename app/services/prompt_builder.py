from datetime import date
from typing import List, Optional
from app.data.srilanka_regions import get_highlights
from app.data.festivals_data import get_festivals_for_dates
from app.data.monsoon_data import get_monsoon_warning

def build_itinerary_prompt(
    start_date: date,
    end_date: date,
    travel_style: str,
    budget_range: str,
    group_size: int,
    regions: List[str],
    interests: List[str],
    starting_point: str,
    special_notes: Optional[str] = None
) -> str:

    total_days = (end_date - start_date).days + 1
    start_month = start_date.month
    end_month   = end_date.month

    # Get festivals
    festivals = get_festivals_for_dates(
        start_month, end_month, regions or ["Island-wide"])

    festival_text = ""
    if festivals:
        names = [f["name"] for f in festivals]
        festival_text = f"""
FESTIVALS DURING THIS TRIP:
{chr(10).join(f"- {f['name']} ({f['category']}): {f['description']}. Tip: {f['tip']}" for f in festivals)}
IMPORTANT: Incorporate these festivals into the itinerary as special themed days.
"""

    # Monsoon check
    monsoon = get_monsoon_warning(
        regions or [], list(range(start_month, end_month + 1)))
    monsoon_text = ""
    if monsoon["has_warning"]:
        warnings = monsoon["warnings"]
        monsoon_text = f"""
MONSOON WARNING:
{chr(10).join(f"- {w['type']}: Affects {w['affected_regions']}. {w['recommendation']}" for w in warnings)}
IMPORTANT: Adjust the itinerary to avoid heavily affected regions during monsoon.
"""

    # Budget guidance
    budget_guide = {
        "BUDGET":    "Guesthouses (LKR 3000-6000/night), local food, buses",
        "MID_RANGE": "Boutique hotels (USD 40-80/night), good restaurants, private transport",
        "LUXURY":    "Premium resorts (USD 150+/night), fine dining, private vehicle with driver"
    }

    # Interest mapping
    interest_map = {
        "hiking":    "Include Ella Rock, Knuckles, Horton Plains, Adams Peak",
        "wildlife":  "Include Yala safari, Minneriya, Wilpattu, whale watching",
        "beaches":   "Include southern beaches, Mirissa, Hiriketiya, Nilaveli",
        "history":   "Include Sigiriya, Polonnaruwa, Anuradhapura, Galle Fort",
        "food":      "Include Colombo food tour, cooking classes, street food",
        "surfing":   "Include Arugam Bay, Weligama, Hikkaduwa",
        "culture":   "Include Kandy Perahera, temples, local villages",
        "ayurveda":  "Include wellness retreats, herbal treatments"
    }

    interest_notes = [
        interest_map[i.lower()]
        for i in interests
        if i.lower() in interest_map
    ]

    prompt = f"""You are an expert Sri Lanka travel planner with deep local knowledge.

Create a complete {total_days}-day Sri Lanka itinerary with these requirements:

TRIP DETAILS:
- Start date: {start_date} | End date: {end_date} | Total days: {total_days}
- Travel style: {travel_style}
- Budget: {budget_range} ({budget_guide.get(budget_range, "mid-range")})
- Group size: {group_size} people
- Starting point: {starting_point}
- Preferred regions: {", ".join(regions) if regions else "All Sri Lanka"}
- Interests: {", ".join(interests) if interests else "General sightseeing"}
{f"- Special notes: {special_notes}" if special_notes else ""}

INTEREST-BASED SUGGESTIONS:
{chr(10).join(f"- {note}" for note in interest_notes) if interest_notes else "- General sightseeing across Sri Lanka"}

{festival_text}
{monsoon_text}

GEOGRAPHIC RULES (MUST FOLLOW):
- Never put Jaffna and Yala/Mirissa on consecutive days (too far)
- Never put Arugam Bay and Colombo on consecutive days
- Group nearby destinations: Sigiriya + Dambulla + Polonnaruwa
- Kandy → Ella by train is scenic and recommended
- Start and end in Colombo for airport access

HIDDEN GEMS RULE:
- Inject 1 lesser-known hidden gem every 2-3 days
- Examples: Jungle Beach, Ravana Ella Cave, Ambuluwawa Tower,
  Pambahinna Village, Mulkirigala Rock Temple

Return ONLY a valid JSON object (no markdown, no explanation) with this exact structure:
{{
  "tripTitle": "descriptive trip title",
  "totalDays": {total_days},
  "estimatedBudget": <total USD estimate as number>,
  "currency": "USD",
  "monsoonWarning": <null or warning string>,
  "days": [
    {{
      "dayNumber": 1,
      "date": "{start_date}",
      "region": "city name",
      "theme": "day theme",
      "locations": ["place1", "place2", "place3"],
      "accommodation": "hotel/guesthouse name",
      "transport": "transport method",
      "meals": ["breakfast suggestion", "lunch suggestion", "dinner suggestion"],
      "hiddenGem": <null or "gem name — brief description">,
      "festivalEvent": <null or "festival name">,
      "tips": "practical tips for this day",
      "estimatedDayCost": <number in USD per person>
    }}
  ]
}}"""

    return prompt


def build_regenerate_day_prompt(
    day_number: int,
    current_region: str,
    travel_style: str,
    budget_range: str,
    exclude_regions: list
) -> str:
    return f"""You are an expert Sri Lanka travel planner.

Regenerate Day {day_number} of a Sri Lanka trip.

CURRENT DAY: {day_number}
REGION: {current_region}
TRAVEL STYLE: {travel_style}
BUDGET: {budget_range}
EXCLUDE THESE OPTIONS: {", ".join(exclude_regions) if exclude_regions else "none"}

Create a fresh alternative day plan for {current_region}.
Include different locations than typical tourist spots.
Try to include 1 hidden gem.

Return ONLY a valid JSON object:
{{
  "dayNumber": {day_number},
  "region": "{current_region}",
  "theme": "new theme",
  "locations": ["place1", "place2", "place3"],
  "accommodation": "accommodation name",
  "transport": "transport method",
  "meals": ["breakfast", "lunch", "dinner"],
  "hiddenGem": "gem name — description or null",
  "festivalEvent": null,
  "tips": "practical tips",
  "estimatedDayCost": <number>
}}"""