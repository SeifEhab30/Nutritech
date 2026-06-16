# =====================================================
# NutriTech - Food Search Route
# GET /foods/search?q=  ->  macros for a food item.
# Primary source: USDA FoodData Central (free API key via
# env USDA_API_KEY, falls back to DEMO_KEY for testing).
# Also searches the local curated dataset so our Egyptian
# dishes still appear. Gracefully degrades to curated-only
# when USDA is unreachable / over quota.
# =====================================================

import os
from typing import Any, Dict, List, Optional

import httpx
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Query, Request

from app.core.rate_limit import limiter
from app.core.security import get_current_user
from app.models.user import User
from app.nutritech.services.data_loader import get_food_store

load_dotenv()

router = APIRouter(prefix="/foods", tags=["Food Search"])

FDC_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"
# Generic, nutrient-quality datasets (skip noisy branded items).
FDC_DATATYPES = ["Foundation", "SR Legacy", "Survey (FNDDS)"]
# USDA nutrientNumber -> our macro key.
FDC_NUTRIENTS = {"208": "calories", "203": "protein", "205": "carbs", "204": "fat"}


def _macros_block(cal: float, p: float, c: float, f: float) -> Dict[str, float]:
    return {
        "calories": round(cal, 1),
        "protein": round(p, 1),
        "carbs": round(c, 1),
        "fat": round(f, 1),
    }


def _scale(per_100g: Dict[str, float], grams: float) -> Dict[str, float]:
    factor = grams / 100.0
    return {k: round(v * factor, 1) for k, v in per_100g.items()}


def _search_curated(q: str, limit: int) -> List[Dict[str, Any]]:
    df = get_food_store().df
    ql = q.lower().strip()
    # Match the name only — matching usda_description on our tiny 257-item
    # set causes false positives (e.g. "vegetables" -> cottage cheese).
    mask = df["name"].str.lower().str.contains(ql, na=False, regex=False)
    hits = df[mask].head(limit)

    out: List[Dict[str, Any]] = []
    for _, row in hits.iterrows():
        per_100g = _macros_block(
            float(row["kcal_100g"]),
            float(row["protein_100g"]),
            float(row["carbs_100g"]),
            float(row["fat_100g"]),
        )
        serving = float(row.get("serving_g") or 0) or None
        out.append({
            "name": str(row["name"]),
            "source": "curated",
            "serving_g": serving,
            "per_100g": per_100g,
            "per_serving": _scale(per_100g, serving) if serving else None,
        })
    return out


def _parse_fdc_food(food: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    vals = {"calories": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0}
    for n in food.get("foodNutrients", []):
        num = str(n.get("nutrientNumber") or n.get("number") or "")
        key = FDC_NUTRIENTS.get(num)
        if key is not None:
            vals[key] = float(n.get("value") or n.get("amount") or 0)
    if vals["calories"] <= 0:
        return None  # unusable entry
    name = (food.get("description") or "").strip().title()
    serving = food.get("servingSize")
    serving = float(serving) if serving else None
    per_100g = _macros_block(vals["calories"], vals["protein"], vals["carbs"], vals["fat"])
    return {
        "name": name,
        "source": "usda",
        "serving_g": serving,
        "per_100g": per_100g,
        "per_serving": _scale(per_100g, serving) if serving else None,
    }


def _search_usda(q: str, limit: int) -> Dict[str, Any]:
    """Returns {"results": [...], "error": None | "rate_limited" | "unavailable"}."""
    api_key = os.getenv("USDA_API_KEY") or "DEMO_KEY"
    params = {
        "query": q,
        "pageSize": limit,
        "dataType": FDC_DATATYPES,
        "api_key": api_key,
    }
    try:
        resp = httpx.get(FDC_URL, params=params, timeout=8.0)
        if resp.status_code == 429:
            return {"results": [], "error": "rate_limited"}
        resp.raise_for_status()
        data = resp.json()
    except (httpx.HTTPError, ValueError):
        return {"results": [], "error": "unavailable"}

    out: List[Dict[str, Any]] = []
    for food in data.get("foods", []):
        parsed = _parse_fdc_food(food)
        if parsed:
            out.append(parsed)
    return {"results": out, "error": None}


@router.get("/search")
@limiter.limit("30/minute")
def search_foods(
    request: Request,
    q: str = Query(..., min_length=2, max_length=80),
    limit: int = Query(15, ge=1, le=30),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    curated = _search_curated(q, limit)
    usda = _search_usda(q, limit)
    # Curated (our dishes) first, then USDA for breadth.
    return {
        "query": q,
        "results": curated + usda["results"],
        "usda_error": usda["error"],
    }
