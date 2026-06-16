# =====================================================
# NutriTech - Meal Planner Route
# POST /plan/daily  ->  personalized daily plan
# =====================================================

import json
import random
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.rate_limit import limiter
from app.core.security import get_current_user, require_premium
from app.database import get_db
from app.models.saved_plan import SavedPlan
from app.models.user import User
from app.nutritech.services.data_loader import get_food_store
from app.nutritech.utils.pipeline import full_pipeline

router = APIRouter(prefix="/plan", tags=["Meal Planner"])

# Warm the food store (load + cluster + KNN) once at import.
get_food_store()


class PlanRequest(BaseModel):
    meals_per_day: int = 3
    snacks_per_day: int = 0
    # All optional: fall back to the saved profile when omitted.
    cuisine_pref: Optional[str] = None
    diabetes: Optional[bool] = None
    hypertension: Optional[bool] = None
    dislikes: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    seed: Optional[int] = None


def _split(s: Optional[str]) -> List[str]:
    if not s:
        return []
    return [t.strip() for t in str(s).split(",") if t.strip()]


DAY_NAMES = ["Saturday", "Sunday", "Monday", "Tuesday",
             "Wednesday", "Thursday", "Friday"]


def _build_payload(profile, body: PlanRequest) -> Dict[str, Any]:
    """Merge the saved profile with per-request overrides (shared by daily+weekly)."""
    return {
        "age": profile.age,
        "gender": profile.gender,
        "height_cm": profile.height,
        "weight_kg": profile.weight,
        "activity_level": profile.activity_level,
        "general_goal": profile.general_goal,
        "diet_type": profile.diet_type,
        "cuisine_pref": body.cuisine_pref or profile.cuisine_pref or "any",
        "meals_per_day": body.meals_per_day,
        "snacks_per_day": body.snacks_per_day,
        "diabetes": profile.diabetes if body.diabetes is None else body.diabetes,
        "hypertension": (
            profile.hypertension if body.hypertension is None else body.hypertension
        ),
        "dislikes": body.dislikes if body.dislikes is not None else _split(profile.dislikes),
        "allergies": (
            body.allergies if body.allergies is not None else _split(profile.allergies)
        ),
    }


def _daily_response(result: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "final_goal": result["final_goal_used"],
        "daily_calories": result["daily_calories"],
        "daily_protein": result["daily_protein"],
        "daily_carbs": result["daily_carbs"],
        "daily_fat": result["daily_fat"],
        "daily_plan": result["daily_plan"],
    }


@router.post("/daily")
@limiter.limit("20/minute")
def get_daily_plan(
    request: Request,
    body: PlanRequest,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    profile = current_user.profile
    if not profile:
        raise HTTPException(status_code=400, detail="Profile not found")

    payload = _build_payload(profile, body)
    try:
        result = full_pipeline(payload, seed=body.seed)
        return _daily_response(result)
    except ValueError as e:
        # pool-starvation / over-restrictive combos -> user-fixable
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/weekly")
@limiter.limit("8/minute")
def get_weekly_plan(
    request: Request,
    body: PlanRequest,
    current_user: User = Depends(require_premium),
) -> Dict[str, Any]:
    profile = current_user.profile
    if not profile:
        raise HTTPException(status_code=400, detail="Profile not found")

    payload = _build_payload(profile, body)
    # Different seed per day -> natural day-to-day variety.
    base = body.seed if body.seed is not None else random.randint(0, 1_000_000)

    try:
        days: List[Dict[str, Any]] = []
        for i in range(7):
            result = full_pipeline(payload, seed=base + i)
            day = _daily_response(result)
            day["day"] = DAY_NAMES[i]
            day["index"] = i
            days.append(day)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    n = len(days)
    weekly = {
        "avg_calories": round(sum(d["daily_plan"]["total_calories"] for d in days) / n, 1),
        "avg_protein": round(sum(d["daily_protein"] for d in days) / n, 1),
        "avg_carbs": round(sum(d["daily_carbs"] for d in days) / n, 1),
        "avg_fat": round(sum(d["daily_fat"] for d in days) / n, 1),
        "target_calories": round(days[0]["daily_calories"], 1),
        "final_goal": days[0]["final_goal"],
    }
    return {
        "meals_per_day": body.meals_per_day,
        "snacks_per_day": body.snacks_per_day,
        "days": days,
        "weekly": weekly,
    }


# =====================================================
# Saved plan (the user's last generated plan, one per user)
# =====================================================

@router.get("/current")
def get_current_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    saved = db.query(SavedPlan).filter(SavedPlan.user_id == current_user.id).first()
    if not saved:
        raise HTTPException(status_code=404, detail="No saved plan")
    return json.loads(saved.plan_json)


@router.put("/current")
def save_current_plan(
    plan: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    payload = json.dumps(plan)
    saved = db.query(SavedPlan).filter(SavedPlan.user_id == current_user.id).first()
    if saved:
        saved.plan_json = payload
    else:
        saved = SavedPlan(user_id=current_user.id, plan_json=payload)
        db.add(saved)
    db.commit()
    return {"status": "saved"}


@router.delete("/current")
def delete_current_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    db.query(SavedPlan).filter(SavedPlan.user_id == current_user.id).delete()
    db.commit()
    return {"status": "deleted"}


# =====================================================
# Saved weekly plan (stored alongside the daily one)
# =====================================================

@router.get("/weekly/current")
def get_current_weekly(
    current_user: User = Depends(require_premium),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    saved = db.query(SavedPlan).filter(SavedPlan.user_id == current_user.id).first()
    if not saved or not saved.weekly_json:
        raise HTTPException(status_code=404, detail="No saved weekly plan")
    return json.loads(saved.weekly_json)


@router.put("/weekly/current")
def save_current_weekly(
    plan: Dict[str, Any],
    current_user: User = Depends(require_premium),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    payload = json.dumps(plan)
    saved = db.query(SavedPlan).filter(SavedPlan.user_id == current_user.id).first()
    if saved:
        saved.weekly_json = payload
    else:
        # weekly with no daily yet: seed a placeholder daily slot.
        saved = SavedPlan(user_id=current_user.id, plan_json="{}", weekly_json=payload)
        db.add(saved)
    db.commit()
    return {"status": "saved"}
