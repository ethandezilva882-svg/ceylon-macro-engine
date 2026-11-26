import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api, num } from "../api";
import { useFetch } from "../useFetch";
import StatCard from "../components/StatCard";
import TimeChart from "../components/TimeChart";
import { Loading, ErrorBanner } from "../components/Status";

const RANGES = [
  { label: "1Y", years: 1 },
  { label: "5Y", years: 5 },
  { label: "10Y", years: 10 },
  { label: "All", years: null },
];
const YEAR = 365.25 * 24 * 3600 * 1000;
const toT = (d) => Date.parse(d);

function lastTwo(rows, key) {
  const valid = rows.filter((r) => r[key] != null);
  return [valid.at(-1), valid.at(-2)];
}

function windowed(rows, years) {
  if (!years || rows.length === 0) return rows;
  const cutoff = rows[rows.length - 1].t - years * YEAR;
  return rows.filter((r) => r.t >= cutoff);
}

function eventsFor(events, types, rows) {
  if (rows.length === 0) return [];
  const lo = rows[0].t;
  const hi = rows[rows.length - 1].t;
  return events
    .filter((e) => types.includes(e.event_type))
    .map((e) => ({ t: toT(e.date), title: e.title }))
    .filter((e) => e.t >= lo && e.t <= hi);
}

export default function Dashboard() {
  const rates = useFetch(api.rates);
  const inflation = useFetch(api.inflation);
  const fx = useFetch(() => api.exchange("USD"));
  const events = useFetch(api.events);
  const [years, setYears] = useState(5);

  const rateRows = useMemo(
    () => (rates.data ?? []).map((r) => ({ t: toT(r.date), sdfr: num(r.sdfr), slfr: num(r.slfr) })),
    [rates.data]
  );
  const inflRows = useMemo(
    () => (inflation.data ?? []).map((r) => ({ t: toT(r.date), ccpi_yoy: num(r.ccpi_yoy), ncpi_yoy: num(r.ncpi_yoy) })),
    [inflation.data]
  );
  const fxRows = useMemo(
    () => (fx.data ?? []).map((r) => ({ t: toT(r.date), rate: num(r.rate) })),
    [fx.data]
  );

  const error = rates.error || inflation.error || fx.error;
  const loading = rates.loading || inflation.loading || fx.loading;
  if (error) return <div className="container page"><ErrorBanner /></div>;
  if (loading) return <div className="container page"><Loading /></div>;

  const evs = events.data ?? [];

  const [rNow, rPrev] = lastTwo(rates.data, "sdfr");
  const inflKey = inflation.data.some((r) => r.ccpi_yoy != null) ? "ccpi_yoy" : "ncpi_yoy";
  const [iNow, iPrev] = lastTwo(inflation.data, inflKey);
  const [fNow, fPrev] = lastTwo(fx.data, "rate");

  const rateView = windowed(rateRows, years);
  const inflView = windowed(inflRows, years);
  const fxView = windowed(fxRows, years);

  return (
    <div className="container page">
      <h1>Sri Lanka Cost of Living</h1>
      <p className="muted">Policy rates, inflation and the rupee, from CBSL data, updated daily.</p>

      <div className="stat-grid">
        <StatCard
          label="CBSL policy rate (SDFR)"
          value={rNow ? `${num(rNow.sdfr).toFixed(2)}%` : "n/a"}
          delta={rNow && rPrev ? num(rNow.sdfr) - num(rPrev.sdfr) : null}
          unit="pts"
          note="vs previous decision"
          asOf={rNow?.date}
        />
        <StatCard
          label={`Inflation, year on year (${inflKey === "ccpi_yoy" ? "CCPI" : "NCPI"})`}
          value={iNow ? `${num(iNow[inflKey]).toFixed(1)}%` : "n/a"}
          delta={iNow && iPrev ? num(iNow[inflKey]) - num(iPrev[inflKey]) : null}
          unit="pts"
          note="vs previous month"
          asOf={iNow?.date}
        />
        <StatCard
          label="USD / LKR"
          value={fNow ? `${num(fNow.rate).toFixed(2)}` : "n/a"}
          delta={fNow && fPrev ? num(fNow.rate) - num(fPrev.rate) : null}
          unit="LKR"
          note="vs previous record"
          asOf={fNow?.date}
        />
      </div>

      <div className="section-head">
        <h2>Sri Lanka Macro at a Glance</h2>
        <div className="range-buttons" role="group" aria-label="Date range">
          {RANGES.map((r) => (
            <button key={r.label} aria-pressed={years === r.years} onClick={() => setYears(r.years)}>
              {r.label}
            </button>
          ))}
        </div>
      </div>

      <TimeChart
        title="Policy Rate History"
        yLabel="Rate (%)"
        unit="%"
        step
        data={rateView}
        events={eventsFor(evs, ["RATE_HIKE", "RATE_CUT"], rateView)}
        lines={[
          { key: "sdfr", name: "SDFR", color: "#667EEA" },
          { key: "slfr", name: "SLFR", color: "#9F7AEA" },
        ]}
      />
      <TimeChart
        title="Inflation History (year on year)"
        yLabel="Inflation (%)"
        unit="%"
        data={inflView}
        events={eventsFor(evs, ["INFLATION_SPIKE"], inflView)}
        lines={[
          { key: "ccpi_yoy", name: "CCPI", color: "#E53E3E" },
          { key: "ncpi_yoy", name: "NCPI", color: "#A0AEC0" },
        ]}
      />
      <TimeChart
        title="LKR per USD"
        yLabel="LKR per USD"
        data={fxView}
        events={eventsFor(evs, ["LKR_DEPRECIATION"], fxView)}
        lines={[{ key: "rate", name: "USD/LKR", color: "#D69E2E" }]}
      />

      <div className="cta">
        <p>Want to see how this affected YOUR spending?</p>
        <Link className="btn" to="/basket">Build your basket</Link>
      </div>
    </div>
  );
}
