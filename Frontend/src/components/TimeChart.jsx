import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, ReferenceLine,
} from "recharts";

const YEAR = 365.25 * 24 * 3600 * 1000;

export default function TimeChart({ title, yLabel, unit = "", data, lines, events = [], step = false }) {
  const hasData = data.length > 0;
  const span = hasData ? data[data.length - 1].t - data[0].t : 0;
  const tick = (t) =>
    new Date(t).toLocaleDateString(
      "en-GB",
      span < 3 * YEAR
        ? { month: "short", year: "2-digit", timeZone: "UTC" }
        : { year: "numeric", timeZone: "UTC" }
    );

  return (
    <section className="card chart-card">
      <h3>{title}</h3>
      {!hasData ? (
        <p className="muted">No data available for this period. Try a wider range.</p>
      ) : (
        <>
          <ResponsiveContainer width="100%" height={340}>
            <LineChart data={data} margin={{ top: 8, right: 16, bottom: 24, left: 8 }}>
              <CartesianGrid stroke="#E2E8F0" strokeDasharray="3 3" />
              <XAxis
                dataKey="t"
                type="number"
                scale="time"
                domain={["dataMin", "dataMax"]}
                tickFormatter={tick}
                tick={{ fontSize: 12 }}
                label={{ value: "Date", position: "insideBottom", offset: -14, fontSize: 12 }}
              />
              <YAxis
                tick={{ fontSize: 12 }}
                width={56}
                label={{ value: yLabel, angle: -90, position: "insideLeft", fontSize: 12 }}
              />
              <Tooltip
                labelFormatter={(t) => new Date(t).toISOString().slice(0, 10)}
                formatter={(v, name) => [v == null ? "n/a" : `${Number(v).toFixed(2)}${unit}`, name]}
              />
              <Legend verticalAlign="top" height={28} />
              {events.map((e, i) => (
                <ReferenceLine key={`${e.t}-${i}`} x={e.t} stroke="#D69E2E" strokeDasharray="2 3" />
              ))}
              {lines.map((l) => (
                <Line
                  key={l.key}
                  dataKey={l.key}
                  name={l.name}
                  stroke={l.color}
                  strokeWidth={2}
                  dot={false}
                  type={step ? "stepAfter" : "monotone"}
                  connectNulls={false}
                  isAnimationActive={false}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
          <div className="chart-foot">
            {data.length} data points
            {events.length > 0 && ` · ${events.length} detected events marked with amber dotted lines`}
          </div>
        </>
      )}
    </section>
  );
}
