Ceylon Cost of Living Engine

A full-stack web app that tracks how the cost of living in Sri Lanka has changed over time, using only Central Bank of Sri Lanka (CBSL) published data. Users will be able to build a personal spending basket and compare their own inflation experience against the official headline figure.

What it does
Tracks CBSL policy rates (SDFR, SLFR), inflation (CCPI/NCPI), and LKR exchange rates across 14 currencies
Automatically ingests and stores CBSL data with idempotent scrapers (re-runs never create duplicates)
Detects macro events such as rate hikes, rate cuts, inflation spikes, and sharp LKR depreciation
Analyses relationships like "how does inflation move 6 to 12 months after a rate hike" and how LKR depreciation passes through to imported inflation
Personal basket feature: set your own spending weights and see your personal inflation rate vs official CPI
Data sources

All data comes from CBSL or Sri Lanka government publications. No proprietary or third-party financial data.

Data	Source	Format
Policy rates (SDFR/SLFR)	CBSL	Excel
CPI / inflation (CCPI, NCPI)	CBSL	Excel
Exchange rates (14 currencies)	CBSL	HTML table
Tech stack
Backend: Python, FastAPI, Uvicorn
Database: PostgreSQL, SQLAlchemy, Alembic
Scraping: Requests, BeautifulSoup4, openpyxl
Data: Pandas, NumPy
Scheduling: APScheduler
Auth: JWT (python-jose), bcrypt (passlib)
Frontend: React, Vite, Recharts, D3
Project structure
ceylon-macro-engine/
├── Backend/        # FastAPI app, models, database config
├── Frontend/       # React + Vite app
├── Scrapers/       # CBSL rates, CPI, and exchange rate scrapers
├── Data/           # Raw data files
├── Docs/           # Project documentation
└── alembic/        # Database migrations
Setup
Clone the repo
Create and activate a virtual environment: .\Backend\venv\Scripts\activate
Install dependencies: pip install -r requirements.txt
Set up PostgreSQL and create a .env file (see below)
Run migrations: alembic upgrade head
Start the backend: uvicorn Backend.main:app --reload
Start the frontend: cd Frontend && npm run dev
Environment variables
DATABASE_URL=postgresql://user:password@localhost:5432/your_db
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
Status

In active development.

[x] Data layer: CBSL rate, CPI, and exchange rate scrapers
[ ] Database cleanup and new tables (users, baskets, macro events)
[ ] REST API and JWT authentication
[ ] Frontend dashboard and correlation charts
[ ] Personal basket feature
[ ] Deployment
Disclaimer

For educational purposes only. Not financial advice.
