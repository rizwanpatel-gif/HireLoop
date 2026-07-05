# HireLoop

An AI-agent hiring pipeline. HR submits a candidate's resume against a job role; a RAG pipeline scores the match and auto-rejects anything below threshold before it ever reaches the database. Everything past that point (sending the round-1 invite, scheduling, rescheduling, rejecting) is driven by HR chatting in plain English with a LangGraph-orchestrated agent that can genuinely pause mid-conversation and resume later.

Live demo: https://hire-loop-snowy.vercel.app
API docs: https://hireloop-rizwan.duckdns.org/docs

## How it works

1. **Screening.** A resume is chunked and matched against the applied-for role's job description using a local ChromaDB vector store. The most relevant JD excerpts are retrieved and handed to an LLM (via OpenRouter) to score the match. Below the threshold, the candidate is rejected by email and never inserted into the database.
2. **Orchestration.** Above threshold, a LangGraph state machine starts a thread for that candidate. Each node (`ask_round1`, `ask_datetime`, `schedule_round`, `await_freetext`) interrupts and waits for HR's next chat message, checkpointed to SQLite so the graph can pause across HTTP requests, potentially days apart.
3. **Chat interface.** HR never touches a form after the initial submission. A single chat page handles round confirmations, scheduling, rescheduling, ad-hoc status/stat queries, and rejection, all parsed from free text.

## Tech stack

**Backend:** FastAPI, SQLAlchemy, SQLite, LangGraph, ChromaDB, `langchain-text-splitters`, OpenRouter (LLM API), rapidfuzz, slowapi

**Frontend:** React, react-router-dom, driver.js (onboarding walkthrough)

**Deployed on:** Oracle Cloud (Ubuntu, systemd, nginx, Let's Encrypt) for the backend, Vercel for the frontend

## Running it locally

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env`:

```
OPENROUTER_API_KEY=your_openrouter_key
EMAIL_USERNAME=your_email
EMAIL_PASSWORD=your_email_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
FRONTEND_ORIGINS=http://localhost:3000
DATABASE_URL=sqlite:///interview_system.db
MATCH_SCORE_THRESHOLD=60
```

Create the schema and seed demo data:

```bash
python migrate_add_current_round.py
python migrate_add_chat_slot_metadata.py
python migrate_add_hiring_pipeline.py
python seed_demo_data.py
```

Run it:

```bash
uvicorn main:app --reload
```

API docs at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
npm start
```

By default it points at `http://localhost:8000`. To point it at a deployed backend instead, set `REACT_APP_API_URL` in `frontend/.env.local`.

## Project structure

```
backend/
  app/
    routers/            # candidates_standalone, agent_chat, job_roles, dashboard_simple
    services/           # ai_service, matching_service, hiring_graph, command_parser, email_service
    models/             # SQLAlchemy models
  main.py               # FastAPI app entrypoint
  migrate_*.py          # raw-SQLite schema migrations (no Alembic)
  seed_demo_data.py

frontend/
  src/
    components/         # Home, CandidateForm, AgentChat
    onboarding/          # Driver.js-driven guided tour
```
