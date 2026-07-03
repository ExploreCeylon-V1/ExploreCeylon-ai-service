from datetime import date
from typing import List, Optional
from app.data.monsoon_data import get_monsoon_warning
from app.services.db_service import (
    get_destinations,
    get_hidden_gems,
    get_events_trip_sync,
    search_destinations,
    get_nearby_destinations,
    get_nearby_gems,
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
    special_notes: Optional[str] = None,
    from_location: Optional[str] = None,
    to_location: Optional[str] = None
) -> str:

    total_days  = (end_date - start_date).days + 1
    start_month = start_date.month
    end_month   = end_date.month

    # ── Resolve from/to with fallbacks ────────────────────
    traveler_from = from_location or starting_point or "Colombo"
    traveler_to   = to_location or (
        ", ".join(regions) if regions else "Sri Lanka"
    )

    # ── Resolve a geographic center for the trip, so we only send the
    # AI candidates that are actually near where the traveler is going
    # instead of just the top-rated destinations nationwide ─────────
    center = None
    geocode_query = to_location or (regions[0] if regions else None)
    if geocode_query:
        geocode_matches = await search_destinations(geocode_query)
        if geocode_matches:
            top_match = geocode_matches[0]
            if top_match.get("latitude") is not None \
                    and top_match.get("longitude") is not None:
                center = (top_match["latitude"], top_match["longitude"])

    # ── Fetch real data from Spring Boot DB ───────────────
    if center:
        destinations = await get_nearby_destinations(
            center[0], center[1], limit=15)
        gems = await get_nearby_gems(center[0], center[1], limit=10)
    else:
        # No geocoded center resolved (unrecognized destination name) —
        # fall back to the top-rated nationwide lists.
        destinations = await get_destinations()
        gems         = await get_hidden_gems()
    events = await get_events_trip_sync(start_date, end_date)

    # ── DEBUG logs ────────────────────────────────────────
    print(f"[DB] Destinations loaded: {len(destinations)} "
          f"(center={'resolved' if center else 'none'})")
    print(f"[DB] Gems loaded:         {len(gems)}")
    print(f"[DB] Events loaded:       {len(events)}")
    print(f"[TRIP] From: {traveler_from} → To: {traveler_to}")

    # ── Format destinations for prompt (with coordinates, so the AI
    # can reason about real distances instead of guessing) ─────────
    def with_coords(name, lat, lng):
        if lat is not None and lng is not None:
            return f"{name} ({lat:.4f}, {lng:.4f})"
        return name

    dest_names = [
        with_coords(d["name"], d.get("latitude"), d.get("longitude"))
        for d in destinations[:15]
    ]
    dest_text  = ", ".join(dest_names) if dest_names else \
        "Sigiriya, Ella, Kandy, Galle, Yala, Mirissa"

    # ── Format hidden gems for prompt ─────────────────────
    gem_names = [
        with_coords(f"{g['title']} ({g['district']})",
                    g.get("latitude"), g.get("longitude"))
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

    # ── Budget guidance ────────────────────────────────────
    budget_guide = {
        "BUDGET":    "Prefer free/low-cost attractions, local food, "
                     "short-distance routing and affordable activities",
        "MID_RANGE": "Balance paid attractions, comfortable pacing, "
                     "good restaurants and efficient routing",
        "LUXURY":    "Prioritize premium experiences, scenic viewpoints, "
                     "fine dining areas and relaxed pacing"
    }

    # ── Interest notes ─────────────────────────────────────
    interest_map = {
        "hiking":       "Ella Rock, Knuckles, Horton Plains, Adams Peak",
        "wildlife":     "Yala, Minneriya, Wilpattu, whale watching",
        "beaches":      "Mirissa, Hiriketiya, Nilaveli, Unawatuna",
        "history":      "Sigiriya, Polonnaruwa, Anuradhapura, Galle Fort",
        "food":         "Colombo food tour, cooking classes, street food",
        "surfing":      "Arugam Bay, Weligama, Hikkaduwa",
        "culture":      "Kandy Perahera, temples, local villages",
        "ayurveda":     "Wellness retreats, herbal treatments",
        "photography":  "Sigiriya sunrise, tea estates, Galle Fort ramparts, "
                        "Ella Nine Arch Bridge, Dambulla cave murals",
        "relaxation":   "Mirissa beach, Unawatuna, Tangalle, Hikkaduwa lagoon",
    }
    interest_notes = "\n".join(
        f"- {interest_map[i.lower()]}"
        for i in interests
        if i.lower() in interest_map
    ) or "- General sightseeing"

    # ── Travel style notes ─────────────────────────────────
    style_notes = {
        "ADVENTURE":    "Include trekking, rock climbing, white-water rafting, "
                        "surfing or wildlife safaris where possible.",
        "CULTURAL":     "Focus on temples, UNESCO sites, traditional crafts, "
                        "local ceremonies and village visits.",
        "RELAXATION":   "Prioritize beaches, spa retreats, slow-paced days "
                        "and scenic viewpoints.",
        "FAMILY":       "Choose family-friendly activities with short travel "
                        "times between stops. Avoid extreme activities.",
        "HONEYMOON":    "Romantic settings, sunset viewpoints, scenic routes, "
                        "slow-paced days and memorable dining areas.",
        "PILGRIMAGE":   "Include Sri Pada, Kataragama, Anuradhapura sacred city, "
                        "Kandy Temple of the Tooth.",
        "WILDLIFE":     "Yala, Minneriya, Wilpattu national parks, "
                        "whale watching from Mirissa.",
        "PHOTOGRAPHY":  "Golden hour at Sigiriya, Nine Arch Bridge Ella, "
                        "Galle Fort streets, tea estate landscapes, "
                        "Dambulla cave interiors.",
    }
    selected_styles = [
        s.strip().upper()
        for s in travel_style.replace("|", ",").split(",")
        if s.strip()
    ]
    matched_style_notes = [
        style_notes[s] for s in selected_styles if s in style_notes
    ]
    style_note = (
        " ".join(matched_style_notes)
        if matched_style_notes
        else "Balance sightseeing and relaxation."
    )

    prompt = f"""You are an expert Sri Lanka travel planner \
with deep local knowledge.

Create a complete {total_days}-day Sri Lanka itinerary.

═══════════════════════════════════
TRIP DETAILS
═══════════════════════════════════
Start date        : {start_date}
End date          : {end_date}
Total days        : {total_days}
Travel style      : {travel_style}
Style guidance    : {style_note}
Budget            : {budget_range} — {budget_guide.get(budget_range, "")}
Group size        : {group_size} people
Traveler is coming FROM : {traveler_from}
Destination/Region      : {traveler_to}
Interests         : {", ".join(interests) if interests else "General"}
{f"Special notes     : {special_notes}" if special_notes else ""}

═══════════════════════════════════
ROUTING LOGIC
═══════════════════════════════════
- Day 1 : Arrive near {traveler_from} (airport / starting city)
- Focus the itinerary around {traveler_to}
- Final day : Return to {traveler_from} for departure
- Optimize route to minimize backtracking
- Destinations and hidden gems below are listed with real (latitude,
  longitude) coordinates where available — use them to judge actual
  distance and group geographically close places on the same day

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
- Group: Sigiriya + Dambulla + Polonnaruwa together
- Keep Kandy and Ella in a logical sequence if both are included
- Start near {traveler_from} and end near {traveler_from}
- Optimize route to minimize travel time
- Do not recommend hotels, guides, vehicles or transport bookings.
- The traveler will add hotels, guides and vehicles manually later.

Return ONLY valid JSON (no markdown, no explanation):
{{
  "tripTitle": "{total_days} Days — {traveler_from} to {traveler_to}",
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
  "dayNumber"       : {day_number},
  "region"          : "{current_region}",
  "theme"           : "new theme",
  "locations"       : ["place1", "place2", "place3"],
  "meals"           : ["breakfast", "lunch", "dinner"],
  "hiddenGem"       : "gem — description or null",
  "festivalEvent"   : null,
  "tips"            : "practical tips",
  "estimatedDayCost": 0
}}"""
