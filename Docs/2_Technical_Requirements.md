# Ceylon Cost of Living Engine — Technical Requirements Document

**Version:** 1.0  
**Last Updated:** July 2026  

---

## 1. System Architecture

Three-tier web application:

```
[Scrapers / APScheduler] --> [PostgreSQL DB] --> [FastAPI Backend] --> [React Frontend]
```

- Scrapers run on a schedule, write to DB
- FastAPI reads from DB, exposes REST endpoints
- React frontend consumes the API, renders charts and UI

No message queue, no caching layer, no microservices. This is a single-server deployment for a portfolio project, keep it simple.

---

## 2. Backend

### 2.1 Runtime
- Python 3.11+
- FastAPI + Uvicorn

### 2.2 Database
- PostgreSQL 18
- SQLAlchemy 2.x (ORM)
- Alembic (migrations)
- All DB changes go through Alembic migrations, no manual schema edits ever

### 2.3 Auth
- JWT via python-jose
- Password hashing via passlib[bcrypt]
- Token expiry: 30 minutes (configured in .env)
- Auth required only for basket endpoints, all macro/dashboard data is public

### 2.4 Scraping
- requests + BeautifulSoup4 for CBSL Excel URL discovery
- openpyxl for Excel parsing
- No Playwright needed going forward (was only used for CSE, which is dropped)
- All scraper functions must be idempotent: re-running should insert missing records and skip existing ones, never duplicate

### 2.5 Scheduling
- APScheduler (AsyncIOScheduler)
- Run scrapers daily at a configurable time (default: 01:00 Sri Lanka time, UTC+5:30)
- Scheduler runs inside the FastAPI process on startup, not a separate cron job

### 2.6 Data Validation
- Pydantic v2 schemas for all API request/response shapes
- Scraper-level validation before DB insert: reject nulls on required fields, reject values outside plausible ranges (e.g. SDFR > 30% or < 0% is suspicious), log and skip bad records rather than crashing the whole scraper run

### 2.7 Environment Config
- python-dotenv, all secrets in .env, .env is gitignored
- Required env vars:
  - DATABASE_URL
  - SECRET_KEY
  - ALGORITHM
  - ACCESS_TOKEN_EXPIRE_MINUTES

---

## 3. Frontend

### 3.1 Runtime
- Node 18+
- React 18 + Vite

### 3.2 Key Libraries
- Recharts: all time-series charts (rates, inflation, FX)
- D3: anything Recharts can't handle (custom annotations, brushing)
- Axios: API calls
- React Router v6: client-side routing

### 3.3 State Management
- No Redux, no Zustand. React context for auth state (user token), local component state for everything else. This project is not complex enough to justify a global state library.

### 3.4 Routing
```
/                   --> Landing / macro dashboard (public)
/macro              --> Full macro data explorer (public)
/correlation        --> Correlation analysis charts (public)
/events             --> Macro events feed (public)
/basket             --> Personal basket builder (auth required)
/basket/results     --> Personal inflation rate results (auth required)
/login              --> Login page
/register           --> Register page
```

### 3.5 API Base URL
Configured via Vite env var: `VITE_API_BASE_URL=http://localhost:8000` in development.

---

## 4. Data Sources

| Data | Source | Format | Update Frequency |
|------|--------|--------|-----------------|
| CBSL Policy Rates (SDFR/SLFR) | CBSL website (historical Excel download) | Excel (.xlsx) | When CBSL updates (roughly monthly) |
| CPI / Inflation (CCPI, NCPI) | CBSL website (dynamic Excel URL) | Excel (.xlsx) | Monthly |
| Exchange Rates (14 currencies) | CBSL exchange rate table | HTML table | Daily |

All sources are CBSL or Sri Lanka government published. No proprietary or third-party financial data.

---

## 5. API Design

### 5.1 Conventions
- REST, JSON responses
- All dates in ISO 8601 format: `YYYY-MM-DD`
- All monetary/rate values as numbers (not strings)
- HTTP 200 for success, 422 for validation errors, 401 for auth failures, 404 for not found, 500 for server errors
- Public endpoints: no auth header needed
- Protected endpoints: `Authorization: Bearer <token>` header required

### 5.2 Endpoint Summary

**Public:**
```
GET /api/rates?from=YYYY-MM-DD&to=YYYY-MM-DD
GET /api/inflation?from=YYYY-MM-DD&to=YYYY-MM-DD&type=CCPI|NCPI
GET /api/exchange?currency=USD&from=YYYY-MM-DD&to=YYYY-MM-DD
GET /api/events?from=YYYY-MM-DD&to=YYYY-MM-DD
GET /api/correlation/rate-vs-inflation?lag_months=6
GET /api/correlation/lkr-vs-inflation?window_days=90
GET /api/summary  --> latest values for all three indicators
```

**Auth:**
```
POST /api/auth/register
POST /api/auth/login
GET  /api/basket
POST /api/basket
PUT  /api/basket
GET  /api/basket/impact?from=YYYY-MM-DD&to=YYYY-MM-DD
```

---

## 6. Performance Requirements

- Dashboard page initial load: under 2 seconds on a local connection
- API responses for date-ranged queries: under 500ms (data is pre-stored in DB, no live scraping on request)
- Scraper runs: complete within 60 seconds per scraper (CBSL data is small files)
- No caching required at this scale

---

## 7. Security Requirements

- .env never committed to git
- Passwords hashed with bcrypt, never stored plain
- JWT tokens expire in 30 minutes
- No user PII stored beyond email and hashed password
- CORS configured to allow only the frontend origin (localhost in dev, deployed domain in prod)
- No user-uploaded files, no file execution, minimal attack surface

---

## 8. Testing Requirements

- Unit tests for correlation computation functions (rate-lag, FX pass-through)
- Unit tests for scraper validation logic (bad record rejection)
- Integration tests for auth flow (register, login, protected endpoint)
- Integration tests for basket CRUD
- Not required: end-to-end browser tests (overkill for a portfolio project at this stage)
- Test framework: pytest

---

## 9. Deployment (Phase 6 target)

- Single VPS or cloud VM (e.g. DigitalOcean Droplet, AWS EC2 t3.micro)
- Nginx as reverse proxy in front of Uvicorn
- PostgreSQL running on the same server
- Process management: systemd or supervisord for Uvicorn
- Environment variables set on the server, not in any committed file
- HTTPS via Let's Encrypt / Certbot

---

## 10. What Playwright Is No Longer Needed For

Playwright was only used for CSE scraping (dynamic page rendering). All remaining scrapers (CBSL rates, CPI, exchange rates) work with requests + BeautifulSoup4 + openpyxl. Playwright can be removed from requirements.txt when doing the Phase 1 cleanup unless a future scraper specifically needs it.
