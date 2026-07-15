# ceylon-macro-engine
A full stack web app correlating Sri Lankan macro indicators (CBSL rates, inflation, LKR) with CSE market performance
## What it does
- Tracks CBSL policy rates (SDFR, SLFR, OPR), inflation (NCPI/CCPI), and LKR/USD
- Scrapes and stores CSE stock prices, sector indices, and foreign investor flow
- Surfaces correlations like "what happens to banking stocks 30 days after a CBSL rate cut"

## Tech Stack
- **Backend:** Python, FastAPI, Uvicorn
- **Database:** PostgreSQL 18, SQLAlchemy, Alembic
- **Scraping:** Playwright, BeautifulSoup4, Requests
- **Data:** Pandas, NumPy
- **Scheduling:** APScheduler
- **Frontend:** React, Vite, Recharts, D3

## Project Structure
ceylon-macro-engine/
├── Backend/        # FastAPI app, models, database config
├── Frontend/       # React + Vite app
├── Scrapers/       # Data scrapers for CBSL, CSE, LKR/USD
├── Data/           # Raw data files
├── Docs/           # Project documentation
└── alembic/        # Database migrations

## Setup
1. Clone the repo
2. Create and activate venv: `.\Backend\venv\Scripts\activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Set up PostgreSQL and create `.env` with your `DATABASE_URL`
5. Run migrations: `alembic upgrade head`
6. Start backend: `uvicorn Backend.main:app --reload`
7. Start frontend: `cd Frontend && npm run dev`

## Status
Currently in active development — Phase 1 (Data Layer) in progress.