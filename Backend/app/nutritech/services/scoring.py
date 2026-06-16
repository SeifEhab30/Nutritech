# =====================================================
# NutriTech v2 - Candidate Scoring
# The curated dataset is pre-tagged, so this replaces the
# old 626-line recommender: filter by diet_tags / sodium /
# dislikes, then score each food by macro-fit to the goal.
# =====================================================

import re
from typing import Dict, List, Optional

import pandas as pd

from app.nutritech.core.config import (
    ALLERGEN_EXPANSIONS,
    DISLIKE_EXPANSIONS,
    SODIUM_CAP_HYPERTENSION,
)

# final goal -> the diet tag a food must carry to be eligible
GOAL_TAG = {
    "weight_loss_balanced": "wl",
    "weight_loss_high_protein": "wl",
    "weight_gain_balanced": "wg",
    "weight_gain_high_protein": "wg",
    "maintenance_balanced": "balanced",
    "maintenance_high_protein": "balanced",
    "keto": "keto",
    "diabetes": "diab",
}


# =====================================================
# DISLIKES  (shared with knn_substitute)
# =====================================================

def apply_dislikes(
    df: pd.DataFrame,
    dislikes: Optional[List[str]],
    expansions: Optional[Dict[str, List[str]]] = None,
) -> pd.DataFrame:
    """Drop rows whose name matches any (expanded) excluded token.

    Shared by dislikes (DISLIKE_EXPANSIONS) and allergies (ALLERGEN_EXPANSIONS).
    """
    if df is None or df.empty or not dislikes:
        return df
    exp = DISLIKE_EXPANSIONS if expansions is None else expansions
    name = df["name"].astype(str).str.lower()
    mask = pd.Series(True, index=df.index)
    for raw in dislikes:
        token = str(raw).strip().lower()
        if not token:
            continue
        for term in exp.get(token, [token]):
            term = str(term).strip().lower()
            if term:
                mask &= ~name.str.contains(re.escape(term), na=False)
    return df[mask].copy()


# =====================================================
# SCORING  (per-100g macro-fit, vectorized)
# =====================================================

def _raw_score(d: pd.DataFrame, fg: str) -> pd.Series:
    p, c, f = d["protein_100g"], d["carbs_100g"], d["fat_100g"]
    cal, fib, sug, sod = d["kcal_100g"], d["fiber_100g"], d["sugar_100g"], d["sodium_100g"]

    if fg == "weight_loss_balanced":
        return 2.0 * p + 1.2 * fib - 0.03 * cal - 0.30 * sug - 0.002 * sod
    if fg == "weight_loss_high_protein":
        return 2.6 * p + 1.0 * fib - 0.025 * cal - 0.30 * sug - 0.002 * sod
    if fg == "maintenance_balanced":
        return 1.0 * p + 1.0 * fib - 0.15 * sug - 0.002 * sod
    if fg == "maintenance_high_protein":
        return 2.2 * p + 0.8 * fib - 0.20 * sug - 0.002 * sod
    if fg == "weight_gain_balanced":
        return 0.02 * cal + 0.5 * c + 0.6 * f + 0.6 * p - 0.002 * sod
    if fg == "weight_gain_high_protein":
        return 1.8 * p + 0.015 * cal + 0.4 * c + 0.4 * f - 0.002 * sod
    if fg == "keto":
        return 1.6 * f + 1.0 * p - 0.8 * c - 0.5 * sug - 0.002 * sod
    if fg == "diabetes":
        return 2.0 * fib + 1.2 * p - 1.2 * sug - 0.15 * c - 0.002 * sod
    # default / maintenance
    return 1.0 * p + 1.0 * fib - 0.15 * sug - 0.002 * sod


def score_candidates(
    df: pd.DataFrame,
    final_goal: str,
    *,
    cuisine_pref: str = "any",
    dislikes: Optional[List[str]] = None,
    allergies: Optional[List[str]] = None,
    hypertension: bool = False,
    diabetes: bool = False,
) -> pd.DataFrame:
    """Filter foods eligible for the goal and attach a 'score' column.

    Health flags: `diabetes` forces diabetic eligibility/scoring (overrides the
    goal's macro-fit), `hypertension` applies a sodium cap. `allergies` are a
    hard, non-relaxable exclusion; `dislikes` are soft (see the pool guard in
    the pipeline, which may relax them).
    """
    fg = str(final_goal).lower().strip()
    # When diabetic, eligibility + scoring switch to the diabetes profile.
    score_fg = "diabetes" if diabetes else fg
    d = df.copy()

    # 1) diet-tag eligibility (with a graceful relax if too few survive)
    tag = "diab" if diabetes else GOAL_TAG.get(fg, "balanced")
    eligible = d[d["diet_tags"].str.contains(tag, na=False)]
    if len(eligible) >= 12:
        d = eligible
    # else keep full set so the planner still has options

    # 2) sodium hard cap for hypertension
    if hypertension:
        capped = d[d["sodium_100g"] <= SODIUM_CAP_HYPERTENSION]
        if not capped.empty:
            d = capped

    # 3) allergies (hard exclude) then dislikes (soft)
    d = apply_dislikes(d, allergies, ALLERGEN_EXPANSIONS)
    d = apply_dislikes(d, dislikes)
    if d is None or d.empty:
        return d

    # 4) macro-fit score, shifted positive
    d = d.copy()
    raw = _raw_score(d, score_fg)
    d["score"] = raw - float(raw.min()) + 1.0

    # 5) Egyptian-cuisine boost (mild always; stronger if user asked)
    pref = str(cuisine_pref).lower().strip()
    strong = pref in {"egyptian", "arab", "egyptian_arab"}
    is_eg = d["cuisine"].str.lower().eq("egyptian")
    d.loc[is_eg, "score"] *= (1.35 if strong else 1.10)

    return d.sort_values("score", ascending=False).reset_index(drop=True)
