const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

async function getJSON(path) {
  const res = await fetch(`${API_BASE}${path}`);

  if (!res.ok) {
    throw new Error(`${path} failed: ${res.status} ${res.statusText}`);
  }

  return res.json();
}

export function fetchCityStats() {
  return getJSON("/dashboard/city");
}

export function fetchCategoryStats() {
  return getJSON("/dashboard/category");
}

export function fetchSourceStats() {
  return getJSON("/dashboard/source");
}