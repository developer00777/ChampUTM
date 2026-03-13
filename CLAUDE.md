# ChampUTM — Developer Guide

## Project Structure
- `backend/` — FastAPI + PostgreSQL (asyncpg/SQLAlchemy 2.0 async)
- `frontend/` — React 18 + TypeScript + Vite + TailwindCSS v4

## Running Locally

```bash
# Backend (from ChampUTM/backend/)
source .venv/bin/activate
uvicorn app.main:app --reload --port 8001

# Frontend (from ChampUTM/frontend/)
npm install
npm run dev        # http://localhost:3000

# PostgreSQL must be running on port 5433 (see docker-compose.yml)
docker compose up db -d
```

## Dev Credentials
`admin@champions.dev` / `admin123`

## Architecture — SOLID Principles Applied
- `models/`       → SOLID-S: pure SQLAlchemy ORM, no business logic
- `repositories/` → SOLID-O/I/L/D: abstract interfaces + concrete PG implementations
- `schemas/`      → SOLID-S: Pydantic v2 schemas, separate from ORM models
- `services/`     → SOLID-D: depends on repository interfaces, not concrete classes
- `api/v1/`       → SOLID-S: routers only handle HTTP concerns, delegate to services

## Backend Conventions
- All DB operations async (SQLAlchemy 2.0 async + asyncpg)
- Use `get_db_session` FastAPI dependency for all routes
- Use `require_auth()` for protected routes, `require_admin()` for admin-only
- Services use `session.flush()` not `session.commit()` — router controls transaction
- Pydantic v2: `model_config = ConfigDict(from_attributes=True)` for ORM serialization

## Frontend Conventions
- TailwindCSS v4: `@import "tailwindcss"` in `index.css` — NO `tailwind.config.js`
- React Query v5: `useQuery({ queryKey, queryFn })` — no legacy options object
- Auth token stored in localStorage, injected by axios request interceptor
- Components never call API directly — always via hooks (`useUTMLinks`, `useAnalytics`, etc.)
- Strict TypeScript: no `any`, no unused vars/params

## Key Endpoints
```
POST   /api/v1/auth/login               → get JWT
POST   /api/v1/auth/register            → register + get JWT
GET    /api/v1/auth/me                  → current user
POST   /api/v1/utm/links                → create UTM link (auth required)
GET    /api/v1/utm/links                → list links (auth required) ?offset=0&limit=50
GET    /api/v1/utm/links/{id}           → get single link (auth required)
DELETE /api/v1/utm/links/{id}           → delete link (auth required)
GET    /api/v1/utm/analytics            → aggregated analytics (auth required) ?days=30
GET    /r/{short_code}                  → public redirect + click tracking (no auth)
```

## Database Migrations
```bash
cd backend && alembic upgrade head
```

## Environment Variables (`backend/.env`)
```
DATABASE_URL=postgresql+asyncpg://champutm:champutm@localhost:5433/champutm
JWT_SECRET_KEY=your-secret-key-min-32-chars
FRONTEND_URL=http://localhost:3000
DEBUG=true
```
