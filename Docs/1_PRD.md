# Ceylon Cost of Living Engine — PRD v3

**Status:** Rebrand from "Ceylon Macro Engine" (CSE stock correlation tool). CSE stock/index data dropped entirely due to their ToS explicitly prohibiting AI-based scraping. This version is 100% built on CBSL/government-published macroeconomic data, no exchange data, no equities.

**Core idea:** Track how the real cost of living in Sri Lanka has changed over time, using CBSL policy rates, inflation, and exchange rates, and let users build a personalized "basket" to see how inflation has actually hit their specific spending pattern, not just the headline CPI number.

---

## What survives from the old project (no changes needed)
- Phase 0 entirely: repo, folder structure, venv, PostgreSQL 18 setup, React/Vite scaffold, Alembic
- CBSL policy rate scraper (102 historical SDFR/SLFR records, 2000–2026)
- CPI/inflation scraper (CCPI/NCPI Excel auto-discovery)
- Exchange rate scraper (14 currencies, 4,700+ records back to 1986)
- Backend stack: FastAPI, SQLAlchemy, Alembic, python-jose, passlib
- Frontend stack: React, Vite, Recharts, D3, Axios

## What gets removed
- `Scrapers/market_index_scraper.py`
- CSE stock price scraper file (t1-6 era)
- `SectorIndex`, `ForeignFlow`, `StockPrice` models and tables
- Any `/market`, stock-correlation, or stock-portfolio code already written

---

## Phase 1: Data Layer (continued)
- [x] t1-1 to t1-5: schema, models, CBSL rate scraper, CPI scraper, exchange rate scraper — done, unchanged
- [ ] **t1-12:** Migration to drop `sector_indices`, `foreign_flow`, and stock-related tables
- [ ] **t1-13:** Build a CPI sub-group scraper if CBSL/Department of Census and Statistics publishes a food vs non-food vs housing breakdown (more useful for "cost of living" framing than headline CPI alone)
- [ ] **t1-14 (stretch):** Build a fuel price scraper (Ceylon Petroleum Corporation publishes price revisions publicly, this is government-published pricing, not a private exchange's proprietary feed)
- [ ] t1-9: Data validation layer — still needed, generalize across all surviving scrapers, no longer stock-specific
- [ ] t1-10: APScheduler daily refresh — same as before, fewer scrapers to schedule now

## Phase 2: Backend API (rescoped)
- [ ] t2-1: FastAPI structure — unchanged
- [ ] t2-2: `/api/macro` endpoints (rates, inflation, exchange) — unchanged
- [ ] **t2-3 (NEW):** `/api/cost-of-living` endpoints — purchasing power index, "how far does X LKR go" calculator
- [ ] **t2-4 (NEW):** Macro event detection — rate_cut, rate_hike, inflation_spike, lkr_depreciation_spike (drop stock-related event types)
- [ ] **t2-5 (NEW):** Correlation engine v2 — rate change vs inflation lag (e.g. "what happens to inflation 6/12 months after a rate hike"), LKR depreciation vs imported inflation pass-through
- [ ] **t2-6 (NEW):** `/api/correlation` endpoints — same shape as before, different target series (inflation/forex instead of stocks)
- [ ] t2-7: JWT authentication — unchanged
- [ ] **t2-8 (RENAMED):** `/api/basket` endpoints — user builds a personal spending basket (e.g. 40% food, 20% transport, 15% housing, etc), GET `/basket/impact` shows how their specific basket's cost has changed over time vs headline CPI
- [ ] t2-9: Unit tests — unchanged, just retarget at new correlation logic
- [ ] t2-10: CORS/Swagger — unchanged

## Phase 3: Frontend Core (rescoped)
- [ ] t3-1: Router/layout — update routes to `/`, `/dashboard`, `/macro`, `/cost-of-living`, `/correlation`, `/basket`, `/login` (drop `/market`, `/portfolio`)
- [ ] t3-2 to t3-8: same component patterns, different data and copy

## Phase 4: Personal Basket Feature (renamed from Portfolio)
- [ ] t4-1: Auth (register/login) — unchanged
- [ ] **t4-2 (NEW):** User builds a custom basket: categories + weights (food, transport, rent, utilities, etc)
- [ ] **t4-3 (NEW):** `/basket/performance` — shows the user's personalized cost-of-living change over a chosen date range, vs the official CPI for comparison
- [ ] **t4-4 (NEW):** Visual: "your personal inflation rate" vs "official inflation rate" line chart

## Phase 5: Correlation Engine Enhancement
- [ ] t5-1 to t5-5: same structure as before, now studying rate-cut/inflation lag effects, currency depreciation pass-through to import-heavy CPI categories, and crisis-period (2022 default, IMF program) deep dives — no stock data involved anywhere

## Phase 6: Polish, Deploy & Document
- [ ] t6-1 to t6-7: unchanged in structure. README and LinkedIn copy must NOT reference stock correlation or imply CSE data ever existed in the deployed product, since that scope is fully gone. Frame purely as a Sri Lankan macroeconomic / cost-of-living analysis tool.

---

## Open questions for Ethan to decide before Phase 1 cleanup starts
1. Does the CPI sub-group breakdown (food/non-food/housing) actually exist as a scrapeable public source from CBSL or DCS? Needs a quick check before committing t1-13 to the plan.
2. Keep the GitHub repo name `ceylon-macro-engine` or rename it to reflect the new scope (e.g. `ceylon-cost-of-living-engine`)? Renaming is cosmetic but matters for the portfolio framing later.
3. Is the fuel price scraper (t1-14) worth the extra build time, or is it scope creep for a project that's already had one major rescope?
