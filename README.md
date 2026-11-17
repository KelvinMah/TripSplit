# TripSplit

**Plan better together.** An AI-assisted group travel planner built with **React, TypeScript, FastAPI, PostgreSQL, OpenAI API**, and optional **Google Maps Places API**.

> **Portfolio disclosure:** This is a substantial demo implementation, not independently verified evidence for the resume's 500+ preferences, 75% planning-time reduction, or 94% constraint satisfaction across 100+ cases. The repository includes five sample evaluation scenarios, not a 100-case benchmark. It does not implement Google Routes optimization or real booking.

## Features

- Create, list, select, and delete trips; persist data in PostgreSQL.
- Add/remove travelers with interests, exclusions, notes, and per-person budget limits.
- Paste group chat and extract structured preferences using OpenAI (optional), with a deterministic heuristic fallback.
- Detect conflicting interests and incompatible daily budgets.
- Generate repeatable day-by-day activity suggestions scored against group interests and bounded by the strictest budget.
- Browse an optional Google Places search API endpoint (requires a key).
- Responsive React dashboard with itinerary and conflict cards.
- Input validation, API tests, sample evaluation, linting and formatting configuration.

## Architecture

```text
React + TypeScript (Vite)
        |
        | JSON / HTTP
        v
FastAPI (Python)
  |        |            |
  |        |            +-- Google Places Text Search (optional)
  |        +--------------- OpenAI preference extraction (optional)
  +------------------------ PostgreSQL / SQLAlchemy
        |
        +-- Conflict detector + deterministic budget-aware itinerary builder
```

## Run with Docker

Requirements: Docker Desktop with Compose, Node.js 20+ for the frontend.

```powershell
# Run from the repository root
Copy-Item .env.example .env
docker compose up --build -d

# In another terminal
cd frontend
npm install
npm run dev
```

Visit **http://localhost:5173** for the UI, **http://localhost:8000/docs** for interactive API docs, and **http://localhost:8000/api/health** for the health check.

Set `OPENAI_API_KEY` and/or `GOOGLE_MAPS_API_KEY` in `.env` to enable optional external services. API keys are used only by the backend. Do not commit `.env`.

**Important:** The backend creates demo tables automatically at startup. For production use, add Alembic migrations, accounts, authorization, rate limits, observability, and real venue validation.

## Run backend locally

```powershell
docker compose up -d db
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:DATABASE_URL = "postgresql+psycopg://tripsplit:tripsplit@localhost:5432/tripsplit"
uvicorn app.main:app --reload
```

## API endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/api/health` | Health check |
| POST | `/api/trips` | Create a trip |
| GET | `/api/trips` | List trips |
| GET | `/api/trips/{id}` | Retrieve a trip |
| DELETE | `/api/trips/{id}` | Delete a trip |
| POST | `/api/trips/{id}/travelers` | Add a traveler |
| DELETE | `/api/trips/{id}/travelers/{traveler_id}` | Remove a traveler |
| POST | `/api/preferences/extract` | Extract group chat preferences |
| POST | `/api/trips/{id}/generate` | Generate itinerary and conflicts |
| GET | `/api/places/search` | Optional Google Places text search |

## Tests and formatting

```powershell
cd backend
pip install -r requirements.txt
pytest -q
ruff check .

# In a separate terminal
cd frontend
npm install
npm run build
npm run lint
npm run format
```

To run the sample extraction evaluation:

```powershell
cd backend
python ../eval/evaluate.py
```

## Limitations

- The itinerary generator currently chooses **generic activity templates**, not verified venues. Google Places discovery is available through an API endpoint but is not automatically used to replace template stops.
- No Google Maps Routes API integration, travel-time optimization, booking, collaborative authentication, or real-time editing.
- Budget figures are illustrative per-person activity estimates, not live quotes.
- Without OpenAI, the heuristic extractor works best with one `Name: message` per line and a small supported interest vocabulary.
- OpenAI calls incur charges. Google Maps requires billing-enabled credentials.
- No verified claims about 500+ preferences, 75% faster planning, or 94% satisfaction are made by this codebase.

## Repository structure

```text
backend/
  app/
    api/         # HTTP routes
    core/        # Configuration and database
    models/      # SQLAlchemy entities
    schemas/     # Pydantic validation
    services/    # Extraction, planning, Places
  tests/         # API tests
frontend/
  src/
    components/  # Forms
    lib/         # Typed API client
    App.tsx      # Dashboard
    style.css    # Responsive styling
eval/            # Sample evaluation
```

## License

MIT.
