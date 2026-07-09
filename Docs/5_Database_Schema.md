# Ceylon Cost of Living Engine — Database Schema

**Version:** 3.0 (post-rebrand, CSE tables removed)  
**Last Updated:** July 2026  
**DB:** PostgreSQL 18  

---

## Tables to KEEP (unchanged from prior migrations)

### cbsl_rates
Stores historical CBSL policy rate decisions.

```sql
CREATE TABLE cbsl_rates (
    id          SERIAL PRIMARY KEY,
    date        DATE NOT NULL UNIQUE,
    sdfr        NUMERIC(5, 2) NOT NULL,
    slfr        NUMERIC(5, 2) NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_cbsl_rates_date ON cbsl_rates(date);
```

Current data: 102 records, 2000-2026.

---

### inflation_data
Stores monthly CPI/inflation readings.

```sql
CREATE TABLE inflation_data (
    id              SERIAL PRIMARY KEY,
    date            DATE NOT NULL,
    indicator_type  VARCHAR(10) NOT NULL,
    value           NUMERIC(8, 2) NOT NULL,
    yoy_change      NUMERIC(8, 4),
    mom_change      NUMERIC(8, 4),
    created_at      TIMESTAMPTZ DEFAULT now(),
    UNIQUE(date, indicator_type)
);

CREATE INDEX idx_inflation_data_date ON inflation_data(date);
CREATE INDEX idx_inflation_data_type ON inflation_data(indicator_type);
```

---

### exchange_rates
Stores daily LKR exchange rates for multiple currencies.

```sql
CREATE TABLE exchange_rates (
    id          SERIAL PRIMARY KEY,
    date        DATE NOT NULL,
    currency    VARCHAR(10) NOT NULL,
    buying      NUMERIC(12, 4),
    selling     NUMERIC(12, 4),
    created_at  TIMESTAMPTZ DEFAULT now(),
    UNIQUE(date, currency)
);

CREATE INDEX idx_exchange_rates_date ON exchange_rates(date);
CREATE INDEX idx_exchange_rates_currency ON exchange_rates(currency);
```

Current data: 4,700+ records across 14 currencies.

---

## Tables to CREATE (new for this version)

### users
Stores registered users.

```sql
CREATE TABLE users (
    id              SERIAL PRIMARY KEY,
    email           VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_users_email ON users(email);
```

Note: No username field, email is the login identifier. No PII beyond email.

---

### baskets
Stores a user's personalized spending basket. One basket per user (upsert pattern, not versioned).

```sql
CREATE TABLE baskets (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    food_weight     NUMERIC(5, 2) NOT NULL DEFAULT 40.00,
    transport_weight NUMERIC(5, 2) NOT NULL DEFAULT 15.00,
    housing_weight  NUMERIC(5, 2) NOT NULL DEFAULT 20.00,
    healthcare_weight NUMERIC(5, 2) NOT NULL DEFAULT 8.00,
    education_weight NUMERIC(5, 2) NOT NULL DEFAULT 7.00,
    clothing_weight NUMERIC(5, 2) NOT NULL DEFAULT 5.00,
    other_weight    NUMERIC(5, 2) NOT NULL DEFAULT 5.00,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now(),
    UNIQUE(user_id),
    CONSTRAINT positive_weights CHECK (
        food_weight >= 0 AND transport_weight >= 0 AND housing_weight >= 0 AND
        healthcare_weight >= 0 AND education_weight >= 0 AND
        clothing_weight >= 0 AND other_weight >= 0
    )
);
```

---

### macro_events
Stores auto-detected macro events from the data. Populated by the event detection job, not user input.

```sql
CREATE TABLE macro_events (
    id          SERIAL PRIMARY KEY,
    date        DATE NOT NULL,
    event_type  VARCHAR(50) NOT NULL,
    title       VARCHAR(200) NOT NULL,
    description TEXT,
    impact      VARCHAR(10) CHECK (impact IN ('positive', 'negative', 'neutral')),
    source      VARCHAR(200),
    created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_macro_events_date ON macro_events(date);
CREATE INDEX idx_macro_events_type ON macro_events(event_type);
```

**event_type values:**
- `RATE_HIKE` - CBSL raised rates by >= 50bps in one decision
- `RATE_CUT` - CBSL cut rates by >= 50bps in one decision
- `INFLATION_SPIKE` - month-on-month CPI change >= 5%
- `LKR_DEPRECIATION` - LKR/USD dropped >= 5% in a 30-day window
- `INFLATION_NORMALISATION` - inflation drops below a threshold after a sustained spike period

`impact` is a coarse read on whether the event is generally good or bad for the average person. `title` and `description` are auto-generated plain-English strings. No value_before/value_after/change_amount tracking in v1, that's a nice-to-have not a need-to-have.

---

## Tables to DROP (migration needed) - COMPLETE

These were created in Phase 1 for CSE data that is no longer part of the project:

```sql
DROP TABLE IF EXISTS sector_indices;
DROP TABLE IF EXISTS foreign_flow;
DROP TABLE IF EXISTS stock_prices;
```

Done via migration `a1b2c3d4e5f6_drop_cse_tables.py`.

---

## Migration Plan

**Completed migration:** `a1b2c3d4e5f6_drop_cse_tables`

Operations completed:
1. Dropped `sector_indices`
2. Dropped `foreign_flow`
3. Dropped `stock_prices`

`users`, `baskets`, and `macro_events` already exist in the DB from an earlier migration.

---

## Summary of Final Schema

| Table | Purpose | Auth Required |
|-------|---------|--------------|
| cbsl_rates | CBSL policy rate history | No (read public) |
| inflation_data | CPI/NCPI monthly readings | No (read public) |
| exchange_rates | Multi-currency LKR rates | No (read public) |
| users | Registered user accounts | N/A |
| baskets | User personalized spending weights | Yes |
| macro_events | Auto-detected significant events | No (read public) |

---

## Notes

- All timestamps are `TIMESTAMPTZ` (timezone-aware), stored in UTC
- `NUMERIC` used throughout for all financial values, never `FLOAT`
- Foreign keys use `ON DELETE CASCADE` on baskets so deleting a user cleans up their basket automatically
- The sum-to-100 constraint on basket weights is intentionally NOT enforced at the DB layer, it's enforced at the API layer with a proper error message