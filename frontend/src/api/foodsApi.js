import { request } from "./client";

// GET /foods/search?q= — macros for a food (USDA FDC + curated).
export function searchFoods(q, limit = 15) {
  const params = new URLSearchParams({ q, limit: String(limit) });
  return request(`/foods/search?${params.toString()}`);
}
