import { request } from "./client";

// POST /tracker/log — add an intake entry; returns the day's DayResponse.
export function logEntry(payload) {
  return request("/tracker/log", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

// GET /tracker/day — entries + totals + target for a date (default today).
export function getDay(date) {
  return request(`/tracker/day${date ? `?date=${date}` : ""}`);
}

// DELETE /tracker/log/:id — remove an entry; returns the day's DayResponse.
export function deleteEntry(id) {
  return request(`/tracker/log/${id}`, { method: "DELETE" });
}

// GET /tracker/range — per-day macro totals over a range (default last 7 days).
export function getRange(start, end) {
  const qs = [];
  if (start) qs.push(`start=${start}`);
  if (end) qs.push(`end=${end}`);
  return request(`/tracker/range${qs.length ? `?${qs.join("&")}` : ""}`);
}
