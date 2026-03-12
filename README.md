# Text-to-SQL AI Data Analyst

Ask questions in natural language and get answers by generating SQL against a local SQLite database.

## Tech stack

- **Frontend**: Next.js (App Router) + React + Tailwind
- **Backend**: FastAPI (Python)
- **LLM**: Groq (via `GROQ_API_KEY`)
- **Database**: SQLite (`backend/amazon.db`)

## Project structure

- `frontend/`: Next.js UI
- `backend/`: FastAPI API + Text-to-SQL pipeline + SQLite DB

## Prerequisites

- Node.js 18+ (for Next.js)
- Python 3.11+ (recommended)
- A Groq API key

## Setup

### 1) Backend (with `uv`)

Create `backend/.env`:

```bash
GROQ_API_KEY=your_key_here
# Optional: override Groq model
# GROQ_MODEL=llama-3.1-8b-instant
```

Install dependencies and run the API using [`uv`](https://github.com/astral-sh/uv):

```bash
cd backend
uv sync
uv run uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000` (docs at `http://localhost:8000/docs`).

### 2) Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

#### Backend URL (optional)

By default the frontend calls `http://localhost:8000`.
If you run the backend elsewhere, set:

```bash
export NEXT_PUBLIC_BACKEND_URL="http://localhost:8000"
```

## Demo

Example questions you can ask:

- “Total products sold in 2025”
- “Top 5 categories by revenue”
- “Average rating per category”

## Notes

- If Groq returns a “model decommissioned” error, set `GROQ_MODEL` to a supported model name.

