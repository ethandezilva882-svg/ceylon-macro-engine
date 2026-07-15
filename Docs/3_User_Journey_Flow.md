# Ceylon Cost of Living Engine — User Journey Flow

**Version:** 1.0  
**Last Updated:** July 2026  

---

## Journey 1: Casual Visitor (no login)

**Who:** Anyone who lands on the site, no account, no specific goal.

```
Land on homepage
    |
    v
See headline summary cards:
- Current CBSL rate (SDFR/SLFR)
- Latest inflation figure (CCPI or NCPI)
- Current LKR/USD rate
    |
    v
Scroll down to macro dashboard charts:
- Policy rate over time (line chart, 2000-present)
- CPI inflation over time (line chart)
- LKR/USD over time (line chart)
- All three annotated with macro events (rate hikes, IMF entry, etc.)
    |
    v
Option A: Click into /macro for deeper exploration
    --> Select date range
    --> Toggle between CCPI and NCPI
    --> Switch currency pair on FX chart
    |
Option B: Click into /correlation
    --> See pre-computed rate-vs-inflation lag chart
    --> See LKR depreciation vs imported inflation pass-through
    --> Read plain-English explanation of what the correlation means
    |
Option C: Click into /events
    --> Chronological feed of detected macro events
    --> Each event links back to the relevant chart period
    |
Option D: Click "Build My Basket" CTA --> redirected to /login
```

---

## Journey 2: Registered User Building a Basket

**Who:** Someone who wants a personalised cost-of-living analysis.

```
Click "Build My Basket" anywhere on site
    |
    v
/register (if no account)
- Enter email + password
- Submit -> JWT token issued, stored in memory/context
    |
    OR
    |
/login (if existing account)
- Enter email + password
- Submit -> JWT token issued
    |
    v
/basket (basket builder page)
- Shown default category weights (pre-filled to match official CCPI basket)
- Adjust sliders/inputs to match their actual spending:
    Food & Beverages      [default 40%] --> [user sets e.g. 35%]
    Transport & Fuel      [default 15%] --> [user sets e.g. 20%]
    Housing & Utilities   [default 20%] --> [user sets e.g. 25%]
    Healthcare            [default 8%]  --> [user sets e.g. 5%]
    Education             [default 7%]  --> [user sets e.g. 10%]
    Clothing & Personal   [default 5%]  --> [user sets e.g. 3%]
    Other                 [default 5%]  --> [user sets e.g. 2%]
- Weights must sum to 100% (UI enforces this live)
- Click "Save Basket"
    |
    v
POST /api/basket --> basket saved to DB against user account
    |
    v
Redirect to /basket/results
- Select date range (default: last 3 years)
- Chart: "Your personal inflation rate" vs "Official CPI" over time
- Key stat: "Over the selected period, official inflation averaged X%. 
  Based on your basket, you experienced Y%."
- Breakdown table: how much each category contributed to the difference
    |
    v
User can go back to /basket and edit weights at any time
Recalculation is instant (client-side once data is loaded)
```

---

## Journey 3: Student or Researcher Using the Correlation Tool

**Who:** Someone interested in the macro analysis, not the personal basket.

```
Land on /correlation directly (or navigate from nav)
    |
    v
Section 1: Rate Change vs Inflation Lag
- Chart showing CBSL rate decisions on x-axis
- Overlaid inflation trajectory over the following 12 months
- Lag slider: user can select 3 / 6 / 9 / 12 month lag to see correlation shift
- Plain-English summary below chart:
  "Historically, rate hikes in Sri Lanka have taken approximately X months 
  to show a measurable reduction in CPI inflation."
    |
    v
Section 2: LKR Depreciation vs Imported Inflation
- Chart showing LKR/USD depreciation events
- Overlaid CPI (or food sub-index if available) with configurable lag
- Plain-English summary:
  "A 10% drop in the LKR has historically corresponded to approximately 
  a X% rise in CPI over the following Y months."
    |
    v
Section 3: Crisis Period Annotated Timeline (2020-2024)
- Single combined chart showing all three indicators (rates, inflation, LKR)
- Annotated with key events:
  2021-Q4: Rate holds despite early inflation signals
  2022-Q1: Inflation surge begins
  2022-Q2: Emergency rate hike cycle starts
  2022-Q3: LKR depreciation peak
  2022-Q4: IMF program entry
  2023: Gradual stabilisation
  2024-2025: Rate cutting cycle begins
- Static but data-driven, pulls from real DB records
```

---

## Journey 4: Returning User Checking Latest Data

**Who:** Someone who has used the site before and wants to check if anything changed.

```
Land on homepage
    |
    v
Summary cards show latest values with delta vs previous period
    |
    v
/events shows any new macro events detected since last visit
(no login required)
    |
    v
If they have a basket: login, navigate to /basket/results
Results auto-update since the underlying data refreshes daily
```

---

## Error States to Handle

| Situation | What the user sees |
|-----------|-------------------|
| API down / DB unreachable | Error banner: "Data temporarily unavailable, please try again later." Chart areas show a skeleton loader, not a blank crash. |
| No data in selected date range | "No data available for this period." with a suggestion to widen the range. |
| Basket weights don't sum to 100% | Inline validation error on the form, save button disabled until fixed. |
| JWT expired mid-session | Silent redirect to /login with a message "Your session expired, please log in again." |
| Registration with existing email | "An account with this email already exists." |

---

## Navigation Structure

```
Header nav (always visible):
  Logo/Home | Dashboard | Macro | Correlation | Events | [Login / My Basket]

Footer:
  Data source credit: Central Bank of Sri Lanka (CBSL)
  GitHub link
  Disclaimer: "For educational purposes only, not financial advice."
```
