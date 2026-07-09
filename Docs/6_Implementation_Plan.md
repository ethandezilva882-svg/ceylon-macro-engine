
## docs/6_Implementation_Plan.md — Ceylon Cost of Living Engine

**Version:** 1.0
**Scope:** Sequencing for the rest of the build, post-CSE-cleanup.

### Phase 1 cleanup (do this before anything else)

1. **t1-12** — Alembic migration: drop `sector_indices`, `foreign_flow`, `stock_prices` — DONE
2. Delete `Scrapers/market_index_scraper.py`
3. Delete the old CSE stock price scraper file from t1-6
4. Strip `SectorIndex`, `ForeignFlow`, `StockPrice` model classes out of `Backend/models.py` — DONE
5. Remove Playwright from `requirements.txt`
6. Rewrite `README.md`
7. **t1-9** — Generalize the validation layer across the 3 surviving scrapers
8. **t1-10** — APScheduler daily job

### Phase 2: Backend API

1. `users` + `baskets` + `macro_events` tables (macro_events already exists)
2. `/api/macro` endpoints (rates, inflation, exchange)
3. `/api/summary`
4. Macro event detection job (t2-4)
5. `/api/events`
6. Correlation engine v2 (t2-5)
7. `/api/correlation` endpoints
8. Auth (register/login, JWT)
9. `/api/basket` endpoints

### Phase 3: Frontend Core

1. Router/layout, nav shell
2. Homepage summary cards + 3 stacked charts
3. `/macro` explorer page
4. `/correlation` page
5. `/events` feed

### Phase 4: Basket feature

1. `/login`, `/register` pages
2. `/basket` builder UI
3. `/basket/results` page

### Phase 5: Correlation engine enhancement

Polish on top of Phase 2's correlation work, don't start early.

### Phase 6: Deploy & docs

VPS, Nginx, systemd, HTTPS, then final README/LinkedIn copy pass.

### Milestones

- **M1:** Schema clean, scrapers refreshed, no CSE remnants anywhere
- **M2:** Macro API live, homepage renders real data
- **M3:** Correlation engine returns trustworthy numbers
- **M4:** Auth + basket feature end to end
- **M5:** Deployed, README doesn't lie about what the project is

### Non-goals for v1

Dark mode, mobile-optimized charts, multi-basket support, admin panel, caching layer.

