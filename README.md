# 🤖 ExploreCeylon — AI Service

**Python FastAPI + Groq LLaMA 3.3-70b Trip Planner for Sri Lanka**

Group 4 · COM3b33 · University of Ruhuna · 2026

<p>
  <img alt="Python" src="https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white">
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.136.1-009688?logo=fastapi&logoColor=white">
  <img alt="Groq" src="https://img.shields.io/badge/Groq-LLaMA%203.3--70b-F55036?logo=groq&logoColor=white">
  <img alt="Uvicorn" src="https://img.shields.io/badge/Uvicorn-0.46.0-2C3E50">
  <img alt="License" src="https://img.shields.io/badge/License-MIT-yellow.svg">
</p>

---

## 📑 Table of Contents

- [Project Overview](#-project-overview)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Environment Variables](#-environment-variables)
- [API Endpoints](#-api-endpoints)
- [Architecture / How It Works](#-architecture--how-it-works)
- [Prompt Engineering](#-prompt-engineering)
- [Sri Lanka Data](#-sri-lanka-data)
- [Docker](#-docker)
- [Integration with Spring Boot](#-integration-with-spring-boot)
- [License](#-license)

---

## 📖 Project Overview

The ExploreCeylon AI Service is a small **FastAPI microservice** that gives the ExploreCeylon backend access to an LLM (Groq's hosted **LLaMA 3.3-70b**) for trip-related text generation, plus a handful of deterministic, rule-based Sri Lanka travel-data endpoints (monsoon warnings, festival matching, budget estimates) that don't need an LLM call at all.

**How it fits into the platform:** it is a pure backend-to-backend service — nothing in either frontend talks to it directly. The Spring Boot backend's `ItineraryAssemblyService` deterministically decides *what* a trip itinerary contains (which destinations/gems/events, which day, what order, respecting geography and budget) using its own SQL/Java logic; this Python service is only asked, afterwards, to write the *narrative text* — a trip title, a theme and tips per day, and a one-sentence description per stop — for that already-finalized structure.

**Key AI capabilities:**

- ✍️ **Narrative generation** (`/ai/itinerary/narrate`) — writes engaging, tone-matched copy for a fixed day-by-day itinerary structure sent by the backend
- 🔁 **Day regeneration** (`/ai/itinerary/regenerate-day`) — asks the LLM to propose a full alternative day (locations, meals, hidden gem, tips) for a given region/style/budget
- 🌧️ **Monsoon awareness** (`/ai/monsoon-check`) — rule-based (no LLM) SW/NE monsoon warnings per region and month
- 🎉 **Festival matching** (`/ai/festival-suggestions`) — rule-based lookup of Sri Lankan festivals/events overlapping a date range and region list
- 💰 **Budget estimation** (`/ai/budget-estimate`) — rule-based flat-rate cost breakdown per travel style

> ℹ️ **Architecture note:** this service used to plan the *entire* trip itself (geography, day grouping, monsoon-avoidance reasoning, hidden-gem injection) via one large prompt. That responsibility has since moved into the backend's `ItineraryAssemblyService` (deterministic SQL/Java), documented in code comments in both `prompt_builder.py` and the backend's `AiService.java`. As a result, `app/services/db_service.py` (a client for pulling destinations/gems/events/guides straight from the Spring Boot API) and `app/data/srilanka_regions.py` (region metadata + incompatible-consecutive-region rules) are **not currently imported by any router** — they're leftover from that earlier design and are documented below for completeness, not as active integration points.

---

## 🛠️ Tech Stack

| Package | Version |
|---|---|
| `fastapi` | 0.136.1 |
| `uvicorn` | 0.46.0 |
| `openai` | 2.32.0 *(installed but unused — see note below)* |
| `python-dotenv` | 1.2.2 |
| `pydantic` | 2.13.3 |
| `pydantic_core` | 2.46.3 |
| `httpx` | 0.28.1 |
| `annotated-doc` | 0.0.4 |
| `annotated-types` | 0.7.0 |
| `anyio` | 4.13.0 |
| `certifi` | 2026.4.22 |
| `click` | 8.3.3 |
| `colorama` | 0.4.6 |
| `distro` | 1.9.0 |
| `h11` | 0.16.0 |
| `httpcore` | 1.0.9 |
| `idna` | 3.13 |
| `jiter` | 0.14.0 |
| `sniffio` | 1.3.1 |
| `starlette` | 1.0.0 |
| `tqdm` | 4.67.3 |
| `typing-inspection` | 0.4.2 |
| `typing_extensions` | 4.15.0 |

**LLM provider:** [Groq](https://console.groq.com) — model `llama-3.3-70b-versatile`, called directly over `httpx` against Groq's **OpenAI-compatible** chat completions endpoint (`https://api.groq.com/openai/v1/chat/completions`). The `openai` package is listed in `requirements.txt` but `app/services/openai_service.py` (despite its name) makes plain `httpx` calls to Groq and never actually imports the `openai` SDK — it's a leftover dependency, not a second AI provider.

> ⚠️ `requirements.txt` is saved as **UTF-16** in this repo (it reads as garbled bytes if opened as UTF-8) — re-save it as UTF-8 if you regenerate it with `pip freeze`, or tooling that expects a plain-text requirements file may choke on it.

---

## 📂 Project Structure

```
.
├── Dockerfile                        # python:3.11-slim, runs app.main:app on :8000
├── requirements.txt                  # pinned dependencies (saved as UTF-16 — see note above)
├── main.py                           # ⚠️ stale placeholder entry point — NOT what Docker/uvicorn run (see note)
│
└── app/
    ├── main.py                       # Real FastAPI entry point — CORS, router registration, /ai/health
    │
    ├── routers/
    │   ├── itinerary.py              # POST /ai/itinerary/narrate, /ai/itinerary/regenerate-day
    │   ├── monsoon.py                # POST /ai/monsoon-check
    │   ├── budget.py                 # POST /ai/budget-estimate
    │   └── festival.py               # POST /ai/festival-suggestions
    │
    ├── models/
    │   └── request_models.py         # All Pydantic request models (see API Endpoints below)
    │
    ├── services/
    │   ├── openai_service.py         # generate_completion() — calls Groq's chat completions API
    │   ├── prompt_builder.py         # build_narrative_prompt(), build_regenerate_day_prompt()
    │   └── db_service.py             # httpx client for the Spring Boot API — currently unused/legacy (see note above)
    │
    └── data/
        ├── srilanka_regions.py       # Region metadata, coordinates, highlights, travel times — currently unused/legacy
        ├── monsoon_data.py           # SW/NE monsoon months + affected/safe regions, get_monsoon_warning()
        └── festivals_data.py         # Sri Lanka festival calendar, get_festivals_for_dates()
```

> ⚠️ **`main.py` at the repo root is a stale placeholder** — a `/health` + a `/generate-trip` stub that returns `{"status": "pending", ...}` and was never wired to Groq. The Dockerfile and the real app both point at **`app/main.py`** (`app.main:app`), which is the actual, current entry point. Don't run the root `main.py` expecting it to do anything.

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11** (matches the Dockerfile's base image)
- `pip`
- A free [Groq](https://console.groq.com) account and API key
- The [ExploreCeylon backend](../ExploreCeylon-backend) running on `http://localhost:8080` if you want to exercise the full trip-generation flow end-to-end (this service itself doesn't require the backend to be up just to start)

### 1. Clone and enter the project

```bash
git clone <repository-url>
cd ExploreCeylon-ai-service
```

### 2. Create and activate a virtual environment

**Windows (PowerShell / cmd):**
```powershell
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your `.env`

Create a `.env` file in the project root (see [Environment Variables](#-environment-variables) below):

```bash
GROQ_API_KEY=your-groq-api-key-here
APP_PORT=8000
GROQ_MODEL=llama-3.3-70b-versatile
```

### 5. Run the service

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 6. Verify it's running

```bash
curl http://localhost:8000/ai/health
```

Expected response:
```json
{
  "status": "running",
  "service": "ExploreCeylon AI Service",
  "version": "1.0.0"
}
```

**Interactive API docs (Swagger UI):** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## ⚙️ Environment Variables

Read via `os.getenv()` (in `app/services/openai_service.py`, loaded through `python-dotenv`'s `load_dotenv()`):

| Variable | Description | Required |
|---|---|:---:|
| `GROQ_API_KEY` | Your Groq API key — get one free at [console.groq.com](https://console.groq.com) (sign up, create an API key under **API Keys**) | ✅ |
| `APP_PORT` | Port the service listens on (referenced in `.env`; the actual `uvicorn` command still needs `--port` passed explicitly, or a process manager reading this var) | ⬜ |
| `GROQ_MODEL` | Model name intended for use with Groq (present in `.env`, but note `app/services/openai_service.py` currently **hardcodes** `"llama-3.3-70b-versatile"` in the request body rather than reading this variable — set it for documentation/consistency, but changing it alone won't change the model actually called) | ⬜ |

`.env.example`:

```bash
# Get a free API key at https://console.groq.com
GROQ_API_KEY=gsk_your_groq_api_key_here

# Port this service listens on
APP_PORT=8000

# Groq model — currently informational only; the model is hardcoded
# in app/services/openai_service.py as "llama-3.3-70b-versatile"
GROQ_MODEL=llama-3.3-70b-versatile
```

---

## 🔌 API Endpoints

All routes are prefixed `/ai`. This service has no authentication of its own — it's only reachable from the backend's internal network/localhost in this setup.

### `POST /ai/itinerary/narrate`

Writes narrative text for an already-finalized itinerary structure. Called by the backend's `AiService.generateNarrative()`.

**Request body** (`NarrativeRequest`):
```json
{
  "start_date": "2026-08-10",
  "end_date": "2026-08-13",
  "travel_style": "CULTURAL",
  "budget_range": "MID_RANGE",
  "group_size": 2,
  "starting_point": "Colombo",
  "to_location": "Kandy",
  "special_notes": "Interested in tea plantations",
  "days": [
    {
      "dayNumber": 1,
      "date": "2026-08-10",
      "region": "Kandy",
      "stops": [
        { "type": "DESTINATION", "name": "Temple of the Tooth", "slot": "MORNING" },
        { "type": "GEM", "name": "Udawatta Kele Forest Sanctuary", "slot": "AFTERNOON" }
      ]
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "tripTitle": "string",
    "days": [
      {
        "dayNumber": 1,
        "theme": "string",
        "tips": "string",
        "stops": [ { "description": "string" } ]
      }
    ]
  }
}
```

### `POST /ai/itinerary/regenerate-day`

Asks the LLM to freely propose a whole alternative day for a region (used when a traveler rejects a generated day).

**Request body** (`RegenerateDayRequest`):
```json
{
  "trip_id": 42,
  "day_number": 2,
  "current_region": "Ella",
  "exclude_regions": ["Jaffna"],
  "travel_style": "ADVENTURE",
  "budget_range": "MID_RANGE"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "dayNumber": 2,
    "region": "Ella",
    "theme": "new theme",
    "locations": ["place1", "place2", "place3"],
    "meals": ["breakfast", "lunch", "dinner"],
    "hiddenGem": "gem — description or null",
    "festivalEvent": null,
    "tips": "practical tips",
    "estimatedDayCost": 0
  }
}
```

### `POST /ai/monsoon-check`

Rule-based only — no LLM call.

**Request body** (`MonsoonCheckRequest`):
```json
{ "regions": ["Galle", "Mirissa"], "start_date": "2026-07-01", "end_date": "2026-07-15" }
```

**Response:**
```json
{
  "success": true,
  "data": {
    "warnings": [
      {
        "type": "SW_MONSOON",
        "month": 7,
        "affected_regions": ["Galle", "Mirissa"],
        "description": "Southwest monsoon brings heavy rainfall to western and southern Sri Lanka. East coast is ideal during this period.",
        "recommendation": "Consider visiting east coast instead: Arugam Bay, Trincomalee"
      }
    ],
    "has_warning": true
  }
}
```

### `POST /ai/budget-estimate`

Rule-based only — no LLM call. Flat per-day rates by budget tier (see [Prompt Engineering](#-prompt-engineering) for the rate table).

**Request body** (`BudgetEstimateRequest`):
```json
{ "duration_days": 5, "budget_range": "MID_RANGE", "group_size": 2, "regions": ["Kandy", "Ella"] }
```

**Response:**
```json
{
  "success": true,
  "data": {
    "budget_range": "MID_RANGE",
    "duration_days": 5,
    "group_size": 2,
    "per_person_total": 600.0,
    "group_total": 1200.0,
    "currency": "USD",
    "daily_breakdown": { "accommodation": 300, "food": 125, "transport": 100, "activities": 75 },
    "note": "Estimates are approximate. Actual costs may vary by season and availability."
  }
}
```

> ℹ️ This endpoint is no longer part of the live trip-generation flow — the backend's `ItineraryAssemblyService.computeDayCost()` now computes real per-day cost in Java from the actual chosen stops. `/ai/budget-estimate` still exists for any other generic estimate use.

### `POST /ai/festival-suggestions`

Rule-based only — no LLM call.

**Request body** (`FestivalRequest`):
```json
{ "start_date": "2026-08-01", "end_date": "2026-08-20", "regions": ["Kandy"] }
```

**Response:**
```json
{
  "success": true,
  "data": {
    "festivals": [
      {
        "name": "Esala Perahera",
        "category": "FESTIVAL",
        "month": 8,
        "day_range": [1, 15],
        "regions": ["Kandy"],
        "description": "Grand procession with elephants, drummers and fire dancers",
        "tip": "Book tickets and accommodation 3+ months in advance"
      }
    ],
    "count": 1
  }
}
```

### `GET /ai/health`

```json
{ "status": "running", "service": "ExploreCeylon AI Service", "version": "1.0.0" }
```

---

## 🏗️ Architecture / How It Works

```
┌──────────────────┐        ┌───────────────────────────┐
│  Traveler clicks  │        │   Spring Boot Backend      │
│ "Generate AI Trip"│───────▶│                             │
└──────────────────┘        │  ItineraryAssemblyService   │
                             │  (Java) deterministically   │
                             │  picks destinations/gems/   │
                             │  events, assigns each to a  │
                             │  day + time slot, respecting│
                             │  geography, budget & style  │
                             │  — using its own DB/SQL.    │
                             │  No LLM involved yet.        │
                             └─────────────┬───────────────┘
                                           │
                                           │  AiService.generateNarrative(body)
                                           │  POST /ai/itinerary/narrate
                                           ▼
                             ┌───────────────────────────┐
                             │   FastAPI (this service)    │
                             │                             │
                             │  routers/itinerary.py       │
                             │       │                     │
                             │       ▼                     │
                             │  prompt_builder.py           │
                             │  build_narrative_prompt()    │
                             │  — turns the FIXED day/stop  │
                             │    structure into a prompt   │
                             │    asking only for narrative │
                             │    text, not new structure.  │
                             │       │                     │
                             │       ▼                     │
                             │  openai_service.py           │
                             │  generate_completion()       │
                             │       │                     │
                             │       ▼                     │
                             │      Groq API                │
                             │  (llama-3.3-70b-versatile)   │
                             │  response_format=json_object │
                             └─────────────┬───────────────┘
                                           │  strict JSON: title,
                                           │  per-day theme/tips,
                                           │  per-stop descriptions
                                           ▼
                             ┌───────────────────────────┐
                             │   Spring Boot Backend       │
                             │  merges narrative text back  │
                             │  onto the already-decided    │
                             │  structure and persists the  │
                             │  final Trip/TripDay/         │
                             │  TripDayItem rows to          │
                             │  PostgreSQL.                 │
                             └───────────────────────────┘
```

**Step by step:**
1. A traveler requests AI itinerary generation on the frontend, which calls the backend's `POST /api/v1/trips/{id}/generate-ai`.
2. The backend's `ItineraryAssemblyService` deterministically decides the entire day-by-day structure (which destination/gem/event, which day, which time slot) directly from its own database — geography and budget filtering happen here, in Java/SQL, not in a prompt.
3. `AiService.generateNarrative(body)` sends that fixed structure to this FastAPI service's `POST /ai/itinerary/narrate`.
4. `prompt_builder.build_narrative_prompt()` turns it into a prompt that explicitly forbids the LLM from adding, removing, or reordering days/stops — its only job is title/theme/tips/description text in a tone matching the trip's travel style.
5. `openai_service.generate_completion()` calls Groq's chat completions endpoint with `response_format: {"type": "json_object"}` and a system prompt demanding pure JSON, then strips any stray ` ```json ` code-fence wrapping before parsing.
6. The backend receives the narrative JSON, merges it onto the structure it already decided, and saves the finished `Trip` → `TripDay` → `TripDayItem` rows to PostgreSQL.

---

## ✍️ Prompt Engineering

**What data is injected into the narrative prompt** (`prompt_builder.build_narrative_prompt`, from the `NarrativeRequest` the backend sends — nothing is fetched live from `db_service.py`, since that module isn't currently called):
- Group size, travel style, budget range, starting point, destination
- A tone note per travel style (see table below)
- Optional free-text `special_notes` from the traveler
- The full fixed day/stop list: day number, date, region label, and each stop's type (`DESTINATION`/`GEM`/`EVENT`), name, and time slot

**Tone-per-style guidance** (`STYLE_TONE` in `prompt_builder.py`) — this only shapes *how the narrative reads*, not what's included:

| Travel Style | Tone |
|---|---|
| `ADVENTURE` | energetic, thrill-seeking |
| `CULTURAL` | reverent, heritage-focused |
| `RELAXATION` | calm, unhurried |
| `FAMILY` | warm, accessible for all ages |
| `HONEYMOON` | romantic, intimate |
| `PILGRIMAGE` | respectful, spiritual |
| `WILDLIFE` | adventurous, nature-focused |
| `PHOTOGRAPHY` | vivid, visually descriptive |

**Geographic routing rules:** these now live entirely in the backend's `ItineraryAssemblyService` (Java), not in this service's prompts. The `INCOMPATIBLE_CONSECUTIVE` region-pair rules in `app/data/srilanka_regions.py` (e.g. `("Jaffna", "Yala")`, `("Trincomalee", "Mirissa")` — regions too far apart to visit on consecutive days) exist in this codebase but, per the current import graph, aren't wired into any active router; the equivalent logic is understood to be enforced deterministically on the backend instead.

**Monsoon awareness:** `app/data/monsoon_data.py` defines two monsoon systems and answers "is this region affected in this month":

| Monsoon | Months | Affected | Safer alternative |
|---|---|---|---|
| SW Monsoon | May–Sep | West/South coast, Hill Country (Colombo, Galle, Mirissa, Nuwara Eliya, Kandy) | East coast (Arugam Bay, Trincomalee, Jaffna, Batticaloa) |
| NE Monsoon | Oct–Jan | North/East (Trincomalee, Jaffna, Arugam Bay, Batticaloa) | West/South coast (Galle, Mirissa, Colombo, Yala, Nuwara Eliya) |

This is exposed only as its own standalone, rule-based `POST /ai/monsoon-check` endpoint — it is **not** injected into the narrative-generation prompt itself; per `prompt_builder.py`'s own code comment, monsoon handling is applied as a note-only warning appended after generation, by the backend's `TripService`, rather than something the LLM is asked to reason about.

**Budget guidance per travel style:** `app/routers/budget.py` uses a flat per-day-per-person rate table (USD), independent of any LLM call:

| Tier | Hotel | Food | Transport | Activities | Total/day |
|---|---:|---:|---:|---:|---:|
| `BUDGET` | $15 | $10 | $8 | $5 | $38 |
| `MID_RANGE` | $60 | $25 | $20 | $15 | $120 |
| `LUXURY` | $200 | $60 | $50 | $40 | $350 |

**Strict JSON output:** both `generate_completion()`'s system prompt ("Always respond with valid JSON only. No markdown. No explanation. Pure JSON.") and the Groq request's `response_format: {"type": "json_object"}` enforce this. As a defensive extra layer, the code also strips a leading/trailing ` ``` ` code fence (and a `json` language tag) before calling `json.loads()`, in case the model wraps its output anyway.

---

## 🗺️ Sri Lanka Data

`app/data/` contains static, hand-curated reference data:

- **`srilanka_regions.py`** — 12 regions (Colombo, Kandy, Ella, Galle, Sigiriya, Yala, Nuwara Eliya, Mirissa, Arugam Bay, Trincomalee, Jaffna, Anuradhapura) each with district, lat/lng coordinates, a highlights list, and rough inter-region travel times; plus an `INCOMPATIBLE_CONSECUTIVE` list of region pairs too far apart for back-to-back days (e.g. Jaffna↔Yala, Trincomalee↔Mirissa). **Currently unused by any active router** — see the architecture note above.
- **`monsoon_data.py`** — SW Monsoon (May–Sep, affects the west/south/hill country) and NE Monsoon (Oct–Jan, affects the north/east), each with an affected-region list, a safer-alternative region list, and a description; powers `get_monsoon_warning()` behind `/ai/monsoon-check`.
- **`festivals_data.py`** — 8 curated festivals/seasonal events (Sinhala & Tamil New Year, Vesak, Esala Perahera, Elephant Gathering at Minneriya, Kataragama Festival, Diwali, Christmas in Galle Fort, Arugam Bay Surf Season, Whale Watching Season), each with category, month or month-range, applicable regions, description, and a practical tip; powers `get_festivals_for_dates()` behind `/ai/festival-suggestions`.

---

## 🐳 Docker

**`Dockerfile`** (as committed):

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build:**
```bash
docker build -t exploreceylon-ai-service .
```

**Run**, passing your Groq key at container start (don't bake secrets into the image):
```bash
docker run -p 8000:8000 \
  -e GROQ_API_KEY=your-groq-api-key-here \
  -e GROQ_MODEL=llama-3.3-70b-versatile \
  exploreceylon-ai-service
```

Or with an env file:
```bash
docker run -p 8000:8000 --env-file .env exploreceylon-ai-service
```

---

## 🔗 Integration with Spring Boot

The backend's `com.exploreceylon.backend.service.AiService` is the only caller of this service. It holds a `WebClient` (bean name `aiWebClient`) configured with the base URL from the backend's `ai.service.url` property (default `http://localhost:8000`).

```java
// AiService.java
public Mono<JsonNode> generateNarrative(Map<String, Object> body) {
    return aiWebClient.post()
            .uri("/ai/itinerary/narrate")
            .bodyValue(body)
            .retrieve()
            .bodyToMono(JsonNode.class)
            .doOnError(e -> log.error("AI service error: {}", e.getMessage()));
}
```

> ⚠️ The endpoint actually called is **`POST /ai/itinerary/narrate`**, not `/ai/itinerary/generate` — the old `/ai/itinerary/generate` route (which used to let the LLM plan the whole trip's geography itself) has been replaced by the narrative-only endpoint, per the code comments in both `AiService.java` and `app/routers/itinerary.py`.

`AiService` also exposes:
- `checkMonsoon(regions, startDate, endDate)` → `POST /ai/monsoon-check`
- `healthCheck()` → `GET /ai/health`

**Request format Spring Boot sends** to `/ai/itinerary/narrate` — a `Map<String, Object>` built from the trip's already-assembled structure, serialized to match `NarrativeRequest`/`PlannedDay`/`PlannedStop` (see the [`/ai/itinerary/narrate` request example](#post-aiitinerarynarrate) above).

**Response format this service returns** — `{"success": true, "data": {...}}`, deserialized by Spring as a generic `JsonNode`; the backend then reads `data.tripTitle`, `data.days[].theme`, `data.days[].tips`, and `data.days[].stops[].description` and merges them onto the day/stop rows it already created.

---

## 📄 License

Distributed under the **MIT License**.
