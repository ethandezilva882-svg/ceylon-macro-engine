# Ceylon Cost of Living Engine — UI/UX Brief

**Version:** 1.0  
**Last Updated:** July 2026  

---

## 1. Design Philosophy

Clean, data-first, no noise. The data is interesting on its own, the UI's job is to get out of the way and let the charts tell the story. Nothing decorative for its own sake. No fake depth, no unnecessary gradients, no hero illustrations.

The tone should feel like a well-built personal finance tool, not a Bloomberg terminal (too dense, too intimidating) and not a marketing landing page (too cheerful, too vague). Somewhere between those two: serious, legible, trustworthy.

---

## 2. Visual Identity

### 2.1 Colour Palette

**Primary:** Deep teal / slate blue. Something that reads as "financial data tool" without being corporate grey.

Suggested starting point:
```
Background (light mode):  #F8FAFB  (off-white, not pure white)
Surface / card bg:         #FFFFFF
Border / divider:          #E2E8F0
Text primary:              #1A202C
Text secondary:            #4A5568
Accent (brand):            #0F7B6C  (deep teal, the primary interactive colour)
Accent hover:              #0A6359
Chart positive / up:       #38A169  (green)
Chart negative / down:     #E53E3E  (red)
Chart neutral:             #667EEA  (blue-purple, for rate lines)
Annotation / event marker: #D69E2E  (amber)
```

Dark mode is a stretch goal for Phase 6, not required for initial build.

### 2.2 Typography

- **Headings:** Inter or DM Sans, 600 weight. Clean, modern, readable.
- **Body / labels:** Inter, 400 weight, 14-16px.
- **Chart labels / axis ticks:** Inter, 400, 12px.
- **Numbers and data values:** Tabular figures (tnum variant if available), so digits align properly in tables and cards.
- No serif fonts anywhere, this isn't a newspaper.

### 2.3 Logo / Brand

"Ceylon Cost of Living" wordmark, no elaborate icon needed. Possibly a simple LKR symbol (₨) incorporated if it looks clean. Keep it minimal.

---

## 3. Layout Principles

- Max content width: 1280px, centered. Wide enough for charts, not unreadably wide on large monitors.
- Consistent padding: 24px on desktop, 16px on mobile.
- Card-based layout for summary stats, full-width charts below.
- Grid: 12-column CSS grid or Tailwind grid, nothing custom.
- Charts should never be cramped. Give them room. A chart that's too small to read defeats the entire purpose of the app.

---

## 4. Key Screens

### 4.1 Homepage / Dashboard

**Above the fold:**
- 3 summary stat cards in a row:
  - Current SDFR/SLFR (with delta arrow vs previous month)
  - Latest CPI inflation % (with delta)
  - Current LKR/USD rate (with delta)
- Each card has: label, big number, small delta indicator (green arrow up or red arrow down)

**Below the fold:**
- "Sri Lanka Macro at a Glance" section
- 3 stacked or tabbed charts:
  - Policy Rate History
  - Inflation History
  - LKR/USD History
- Each chart has: X-axis (date), Y-axis (value), event annotations as vertical dotted lines with labels on hover
- Date range selector above charts (default: 5 years)

**CTA at bottom of page:**
- "Want to see how this affected YOUR spending? Build your basket." --> /register or /basket

### 4.2 Macro Explorer (/macro)

- Sidebar or top filter bar with:
  - Date range picker (from/to)
  - Indicator toggles: Rates / Inflation / Exchange Rate
  - For inflation: CCPI vs NCPI toggle
  - For FX: currency selector dropdown (USD, EUR, GBP, INR, etc.)
- Main area: selected chart(s) rendered full-width
- Beneath each chart: a data table showing the raw values for the selected period (date, value, change)
- "Download CSV" button for the table data (nice to have for portfolio demo purposes)

### 4.3 Correlation (/correlation)

- Two main sections, each with:
  - Chart (full width)
  - Plain-English explanation paragraph beneath it (not hidden, always visible)
- Section 1: Rate vs Inflation Lag
  - Lag selector: 3 / 6 / 9 / 12 months (tab or radio button, not a full date picker)
- Section 2: LKR Depreciation vs CPI Pass-Through
  - Window selector: 30 / 60 / 90 days
- Section 3: Crisis Period Timeline (static, no selector needed)
  - Combined 3-series chart with annotated events
  - Event list below the chart in a simple timeline format

### 4.4 Events Feed (/events)

- Chronological list, newest first
- Each event card:
  - Event type badge (RATE_HIKE / RATE_CUT / INFLATION_SPIKE / LKR_DEPRECIATION / INFLATION_NORMALISATION)
  - Date
  - Plain-English description ("CBSL raised the SDFR by 100bps to 14.5% on [date]")
  - "View on chart" link that takes you to /macro with the right date range pre-loaded
- Filter by event type (checkboxes at top)

### 4.5 Basket Builder (/basket)

- Auth-gated, redirect to /login if not logged in
- Category weight inputs: either sliders with number inputs beside them, or just number inputs
- Live "total" display that shows current sum, turns red if over/under 100%, green when exactly 100%
- Save button disabled until weights sum to 100%
- Below the form: brief explanation of what the basket is used for, referencing the official CBSL CPI basket weights as a starting reference

### 4.6 Basket Results (/basket/results)

- Date range selector at top (default: 2020-present to cover the crisis period)
- Main chart: dual-line chart showing "Your basket inflation rate" (custom colour) vs "Official CCPI" (grey)
- Summary stats:
  - "Official average inflation over period: X%"
  - "Your basket average inflation over period: Y%"
  - Difference and what it means in plain English
- Breakdown table: each category, its weight, the sub-index inflation, and contribution to total

---

## 5. Chart Design Standards

- Library: Recharts as primary (already in stack), D3 for anything Recharts can't handle
- All charts must have:
  - Descriptive title above
  - X and Y axis labels (not just tick marks)
  - A tooltip on hover showing date and value(s)
  - A legend when showing multiple series
- Annotation markers (macro events): vertical dotted line in amber (#D69E2E), label shown on hover
- Colour consistency across the app:
  - SDFR line: #667EEA (blue-purple)
  - SLFR line: #9F7AEA (lighter purple)
  - Inflation: #E53E3E (red)
  - LKR/USD: #D69E2E (amber)
  - User basket: #0F7B6C (teal, the brand colour)
  - Official CPI comparison: #A0AEC0 (grey)

---

## 6. Responsive Behaviour

- Desktop first (this is a data tool, most use will be on desktop)
- Mobile: charts stack vertically, summary cards stack vertically, nav collapses to hamburger
- Minimum supported width: 375px (standard mobile)
- Charts on mobile: maintain readability, simplify if necessary (e.g. hide some annotation labels)

---

## 7. Accessibility Minimums

- All form inputs have labels (no placeholder-only inputs)
- Colour is never the only indicator of meaning (use labels alongside colour on chart legends)
- Tab navigation works through the main flows
- Font sizes: minimum 14px for any readable text

---

## 8. What to Avoid

- Dark patterns or fake urgency
- Excessive loading skeletons (one simple spinner or skeleton per chart is fine)
- Modal overload (use inline errors, not popups for form validation)
- Animations on data elements (charts just render, no animated counting numbers or flying bars)
- Cluttered navbars with dropdowns inside dropdowns
- Footer with 47 links nobody reads
