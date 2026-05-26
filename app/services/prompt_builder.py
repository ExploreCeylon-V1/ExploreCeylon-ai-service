from datetime import date
from typing import List, Optional
from app.data.monsoon_data import get_monsoon_warning
from app.services.db_service import (
    get_destinations,
    get_hidden_gems,
    get_events,
    get_guides
)

async def build_itinerary_prompt(
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

    total_days   = (end_date - start_date).days + 1
    start_month  = start_date.month
    end_month    = end_date.month

    # ── Fetch real data from Spring Boot DB ───────────────
    destinations = await get_destinations()
    gems         = await get_hidden_gems()
    events       = await get_events(
        month=start_month, region=None)

    # ── Format destinations for prompt ────────────────────
    dest_names = [d["name"] for d in destinations[:15]]
    dest_text  = ", ".join(dest_names) if dest_names else \
        "Sigiriya, Ella, Kandy, Galle, Yala, Mirissa"

    # ── Format hidden gems for prompt ─────────────────────
    gem_names = [
        f"{g['title']} ({g['district']})"
        for g in gems[:10]
    ]
    gems_text = "\n".join(
        f"- {g}" for g in gem_names
    ) if gem_names else \
        "- Jungle Beach (Galle)\n- Ravana Ella Cave (Ella)"

    # ── Format events for prompt ──────────────────────────
    event_names = [
        f"{e['title']} — {e['region']} "
        f"({e['startDate']} to {e['endDate']})"
        for e in events[:8]
    ]
    events_text = "\n".join(
        f"- {e}" for e in event_names
    ) if event_names else "No major events during travel period"

    # ── Monsoon check ──────────────────────────────────────
    monsoon = get_monsoon_warning(
        regions or [],
        list(range(start_month, end_month + 1))
    )
    monsoon_text = ""
    if monsoon["has_warning"]:
        warnings = monsoon["warnings"]
        monsoon_text = f"""
⚠️ MONSOON WARNING:
{chr(10).join(
    f"- {w['type']}: Affects {w['affected_regions']}. "
    f"{w['recommendation']}"
    for w in warnings
)}
IMPORTANT: Adjust itinerary to avoid affected regions.
"""
        
    # ── Fetch real data from Spring Boot DB ───────────────
    destinations = await get_destinations()
    gems         = await get_hidden_gems()
    events       = await get_events(month=start_month, region=None)

    # ── DEBUG — add these 3 lines ─────────────────────────
    print(f"[DB] Destinations loaded: {len(destinations)}")
    print(f"[DB] Gems loaded: {len(gems)}")
    print(f"[DB] Events loaded: {len(events)}")

    # ── Budget guidance ────────────────────────────────────
    budget_guide = {
        "BUDGET":    "Guesthouses LKR 3000-6000/night, "
                     "local food, buses",
        "MID_RANGE": "Boutique hotels USD 40-80/night, "
                     "good restaurants, private transport",
        "LUXURY":    "Premium resorts USD 150+/night, "
                     "fine dining, private vehicle with driver"
    }

    # ── Interest notes ─────────────────────────────────────
    interest_map = {
        "hiking":    "Ella Rock, Knuckles, Horton Plains, Adams Peak",
        "wildlife":  "Yala, Minneriya, Wilpattu, whale watching",
        "beaches":   "Mirissa, Hiriketiya, Nilaveli, Unawatuna",
        "history":   "Sigiriya, Polonnaruwa, Anuradhapura, Galle Fort",
        "food":      "Colombo food tour, cooking classes, street food",
        "surfing":   "Arugam Bay, Weligama, Hikkaduwa",
        "culture":   "Kandy Perahera, temples, local villages",
        "ayurveda":  "Wellness retreats, herbal treatments"
    }
    interest_notes = "\n".join(
        f"- {interest_map[i.lower()]}"
        for i in interests
        if i.lower() in interest_map
    ) or "- General sightseeing"

    prompt = f"""You are an expert Sri Lanka travel planner 
with deep local knowledge.

Create a complete {total_days}-day Sri Lanka itinerary.

═══════════════════════════════════
TRIP DETAILS
═══════════════════════════════════
Start date    : {start_date}
End date      : {end_date}
Total days    : {total_days}
Travel style  : {travel_style}
Budget        : {budget_range} — {budget_guide.get(budget_range, "")}
Group size    : {group_size} people
Starting point: {starting_point}
Regions       : {", ".join(regions) if regions else "All Sri Lanka"}
Interests     : {", ".join(interests) if interests else "General"}
{f"Special notes : {special_notes}" if special_notes else ""}

═══════════════════════════════════
REAL DESTINATIONS (from database)
═══════════════════════════════════
Use these verified Sri Lanka destinations:
{dest_text}

═══════════════════════════════════
REAL HIDDEN GEMS (from database)
═══════════════════════════════════
Inject 1 hidden gem every 2-3 days from this list:
{gems_text}

═══════════════════════════════════
REAL EVENTS (from database)
═══════════════════════════════════
{events_text}
Incorporate matching events into relevant days.

{monsoon_text}

═══════════════════════════════════
INTEREST-BASED SUGGESTIONS
═══════════════════════════════════
{interest_notes}

═══════════════════════════════════
GEOGRAPHIC RULES (MUST FOLLOW)
═══════════════════════════════════
- Never put Jaffna + Yala/Mirissa on consecutive days
- Never put Arugam Bay + Colombo on consecutive days
- Group: Sigiriya + Dambulla + Polonnaruwa
- Kandy → Ella by train is scenic — recommend it
- Start and end in Colombo (airport)
- Optimize route to minimize travel time

Return ONLY valid JSON (no markdown):
{{
  "tripTitle": "descriptive title",
  "totalDays": {total_days},
  "estimatedBudget": <total USD number>,
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
      "meals": ["breakfast", "lunch", "dinner"],
      "hiddenGem": <null or "gem — description">,
      "festivalEvent": <null or "festival name">,
      "tips": "practical tips",
      "estimatedDayCost": <USD per person number>
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

Regenerate Day {day_number} for region: {current_region}

TRAVEL STYLE : {travel_style}
BUDGET       : {budget_range}
EXCLUDE      : {", ".join(exclude_regions) if exclude_regions else "none"}

Create a fresh alternative day with different locations.
Include 1 hidden gem if possible.

Return ONLY valid JSON:
{{
  "dayNumber"      : {day_number},
  "region"         : "{current_region}",
  "theme"          : "new theme",
  "locations"      : ["place1", "place2", "place3"],
  "accommodation"  : "name",
  "transport"      : "method",
  "meals"          : ["breakfast", "lunch", "dinner"],
  "hiddenGem"      : "gem — description or null",
  "festivalEvent"  : null,
  "tips"           : "practical tips",
  "estimatedDayCost": 0
}}"""

