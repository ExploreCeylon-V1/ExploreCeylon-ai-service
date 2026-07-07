from app.models.request_models import NarrativeRequest

# ── Tone/voice guidance per travel style ────────────────────────────
# Content selection (which stops, which day, geography/corridor) is now
# decided entirely by the backend's ItineraryAssemblyService before this
# prompt is ever built — these notes only shape *how the narrative
# reads*, which still matters and stays.
STYLE_TONE = {
    "ADVENTURE":   "energetic, thrill-seeking tone",
    "CULTURAL":    "reverent, heritage-focused tone",
    "RELAXATION":  "calm, unhurried tone",
    "FAMILY":      "warm, accessible tone for all ages",
    "HONEYMOON":   "romantic, intimate tone",
    "PILGRIMAGE":  "respectful, spiritual tone",
    "WILDLIFE":    "adventurous, nature-focused tone",
    "PHOTOGRAPHY": "vivid, visually descriptive tone",
}


def _style_tone_note(travel_style: str) -> str:
    selected = [
        s.strip().upper()
        for s in travel_style.replace("|", ",").split(",")
        if s.strip()
    ]
    notes = [STYLE_TONE[s] for s in selected if s in STYLE_TONE]
    return ", ".join(notes) if notes else "balanced, friendly tone"


def build_narrative_prompt(request: NarrativeRequest) -> str:
    """Builds a short, narrative-only prompt. The day/stop structure
    (which places, which day, what order) is already final — the LLM's
    only job is to write an engaging theme + tips per day and a short
    description per stop, in the requested tone, without touching the
    structure itself.

    This replaces the old build_itinerary_prompt(), which asked the LLM
    to plan the whole trip (geography, day-grouping, hidden gem
    injection, festival matching) via a long hard-coded prompt (a
    "GEOGRAPHIC RULES" block, interest/style content-selection maps,
    monsoon-avoidance prose). That responsibility moved to
    ItineraryAssemblyService (backend) so corridor/budget/style
    filtering happens deterministically in SQL/Java instead of being
    hinted at in prose the LLM could ignore. Monsoon handling is
    unchanged — it stays a note-only warning appended after generation
    by TripService, not something this prompt needs to reason about.
    """
    tone = _style_tone_note(request.travel_style)
    traveler_to = request.to_location or "Sri Lanka"

    days_block_lines = []
    for day in request.days:
        stops_lines = "\n".join(
            f"    {i + 1}. [{stop.type}] {stop.name} ({stop.slot})"
            for i, stop in enumerate(day.stops)
        ) or "    (no stops this day)"
        region_suffix = f" — {day.region}" if day.region else ""
        days_block_lines.append(
            f"  Day {day.dayNumber} — {day.date}{region_suffix}\n{stops_lines}"
        )
    days_block = "\n".join(days_block_lines)

    first_day_number = request.days[0].dayNumber if request.days else 1

    prompt = f"""You are a Sri Lanka travel copywriter. The itinerary \
below is ALREADY FINAL — the places, their order, and which day each \
belongs to were chosen by the trip-planning system. Do NOT add, \
remove, reorder or rename any day or stop. Your only job is to write \
engaging narrative text for it.

Trip: {request.group_size} people, {request.travel_style} style, \
{request.budget_range} budget, from {request.starting_point} to \
{traveler_to}.
Writing tone: {tone}.
{f"Special notes: {request.special_notes}" if request.special_notes else ""}

FIXED ITINERARY (do not change structure):
{days_block}

For each day, write:
- "theme": a short (3-6 word) catchy day theme
- "tips": one or two practical sentences (what to wear/bring, timing, etc.)
For each stop, write:
- "description": one engaging sentence about that specific stop, matching the tone above

Also write a short overall "tripTitle" for the whole trip.

Return ONLY valid JSON (no markdown, no explanation), with EXACTLY the \
same number of days and EXACTLY the same number of stops per day, in \
the same order, as the fixed itinerary above:
{{
  "tripTitle": "string",
  "days": [
    {{
      "dayNumber": {first_day_number},
      "theme": "string",
      "tips": "string",
      "stops": [
        {{ "description": "string" }}
      ]
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
