# AI Customer Support Agent (Mock AI)

Manage support tickets, classify priority, retrieve local knowledge-base guidance, and simulate safe escalation.

## What this is

This is a self-contained full-stack sample for testing an FDE repository/application evaluator. The mock AI classifies tickets with transparent keyword rules and searches a bundled knowledge base. No external services or API keys are used.

## Stack
- React + Vite frontend
- Python FastAPI backend
- SQLite local database (seeded on startup)
- Docker Compose
- pytest smoke tests

## Run with Docker

```bash
docker compose up --build
```

Open http://localhost:5173. API docs: http://localhost:8000/docs. Health check: http://localhost:8000/api/health. No API keys or external AI services are required.

## Run locally without Docker

Backend (Python 3.11+):
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend (Node 20+): in another terminal run `cd frontend && npm install && npm run dev`.

## Test backend

```bash
cd backend
pytest -q
```

## Evaluation scenarios
- Create and list support tickets
- Rule-based category and priority classification
- Search local knowledge base for suggested response
- Escalate sensitive or unresolved issues
- Invalid inputs should return validation errors.
- Empty/no-match results should be handled without crashing.
- Refreshing the browser should retain persisted records (SQLite).
- API errors should not silently appear as successful results.
- Inspect whether the UI clearly labels mock AI output and its limitations.

## Limitations
This is a sample benchmark, not a production-ready system. The AI behavior is deterministic and limited; there is no real model inference, external integration, or claim of semantic understanding. Add stronger auth, migrations, observability, and broader tests for production use.
