export default function StatCard({ label, value, delta, unit, note, asOf }) {
  let deltaText = "No previous value to compare";
  if (delta != null) {
    if (Math.abs(delta) < 1e-9) {
      deltaText = `No change ${note}`;
    } else {
      const arrow = delta > 0 ? "▲" : "▼";
      deltaText = `${arrow} ${Math.abs(delta).toFixed(2)} ${unit} ${note}`;
    }
  }
  return (
    <div className="card">
      <div className="stat-label">{label}</div>
      <div className="stat-value">{value}</div>
      <div className="stat-delta">{deltaText}</div>
      {asOf && <div className="stat-asof">As of {asOf}</div>}
    </div>
  );
}
