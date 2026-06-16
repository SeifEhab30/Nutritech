import { request } from "./client";

// POST /plan/daily — generate a personalized daily plan.
export function generatePlan(payload) {
  return request("/plan/daily", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

// POST /substitute/ — KNN-swap one food in an existing plan.
export function substituteFood(payload) {
  return request("/substitute/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

// POST /substitute/options — candidate swaps for one food.
export function substituteOptions(payload) {
  return request("/substitute/options", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

// POST /macros/calculate — compute macros without persisting the profile.
export function calculateMacros(payload) {
  return request("/macros/calculate", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

// GET /plan/current — the user's last saved plan (404 if none).
export function getCurrentPlan() {
  return request("/plan/current");
}

// PUT /plan/current — persist the current plan.
export function saveCurrentPlan(plan) {
  return request("/plan/current", {
    method: "PUT",
    body: JSON.stringify(plan),
  });
}

// POST /plan/weekly — generate a 7-day plan.
export function generateWeeklyPlan(payload) {
  return request("/plan/weekly", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

// GET /plan/weekly/current — the user's last saved weekly plan (404 if none).
export function getCurrentWeekly() {
  return request("/plan/weekly/current");
}

// PUT /plan/weekly/current — persist the current weekly plan.
export function saveCurrentWeekly(plan) {
  return request("/plan/weekly/current", {
    method: "PUT",
    body: JSON.stringify(plan),
  });
}
