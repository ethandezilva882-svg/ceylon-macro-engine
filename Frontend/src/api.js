const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api";

async function get(path, params) {
  const url = new URL(BASE + path);
  if (params) {
    Object.entries(params).forEach(([k, v]) => {
      if (v != null) url.searchParams.set(k, v);
    });
  }
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

const byDate = (a, b) => (a.date < b.date ? -1 : a.date > b.date ? 1 : 0);

export const api = {
  rates: () => get("/rates").then((r) => [...r].sort(byDate)),
  inflation: () => get("/inflation").then((r) => [...r].sort(byDate)),
  exchange: (currency = "USD") =>
    get("/exchange", { currency }).then((r) =>
      r.filter((x) => x.currency === currency).sort(byDate)
    ),
  events: () => get("/events").then((r) => [...r].sort(byDate)),
  summary: () => get("/summary"),
};

// The API returns decimals as strings ("9.00"), so convert before any maths.
export const num = (v) => (v == null ? null : Number(v));
