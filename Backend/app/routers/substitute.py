# =====================================================
# NutriTech - Substitute Route
# POST /substitute/          -> swap a food (top match or a chosen one)
# POST /substitute/options   -> list candidate swaps to choose from
# =====================================================

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.nutritech.services.data_loader import get_food_store
from app.nutritech.services.knn_substitute import (
    apply_named_substitute,
    get_substitute_options,
    replace_disliked_in_daily_plan,
)

router = APIRouter(prefix="/substitute", tags=["Meal Substitution"])


class SubstituteRequest(BaseModel):
    plan: Dict[str, Any] = Field(..., description="Existing daily plan dictionary")
    disliked_name: str = Field(..., description="Exact name of the food to replace")
    # If set, swap to this specific food (from the options list); else top match.
    replacement_name: Optional[str] = None
    dislikes: Optional[List[str]] = []
    prefer_same_cluster: bool = True


class OptionsRequest(BaseModel):
    plan: Dict[str, Any]
    food_name: str
    dislikes: Optional[List[str]] = []


@router.post("/options")
def substitute_options(request: OptionsRequest) -> Dict[str, Any]:
    store = get_food_store()
    try:
        options = get_substitute_options(
            request.plan, request.food_name, store, dislikes=request.dislikes
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"options": options}


@router.post("/")
def substitute_food(request: SubstituteRequest) -> Dict[str, Any]:
    store = get_food_store()
    try:
        if request.replacement_name:
            updated = apply_named_substitute(
                request.plan, request.disliked_name, request.replacement_name, store
            )
        else:
            updated = replace_disliked_in_daily_plan(
                plan=request.plan,
                disliked_name=request.disliked_name,
                store=store,
                dislikes=request.dislikes,
                prefer_same_cluster=request.prefer_same_cluster,
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"updated_plan": updated}
