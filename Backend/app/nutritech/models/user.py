# =====================================================
# NutriTech - User Profile Model
# Profile builder, BMI, BMR, TDEE calculations
# =====================================================

from typing import Any, Dict, List

from app.nutritech.core.config import ACTIVITY_MAP, DISLIKE_EXPANSIONS, clamp_meal_counts


# =====================================================
# HELPERS
# =====================================================

def _normalize_list_like(x: Any) -> List[str]:
    if x is None:
        return []
    if isinstance(x, str):
        return [t.strip().lower() for t in x.split(",") if t.strip()]
    if isinstance(x, (list, tuple, set)):
        out: List[str] = []
        for v in x:
            if v is None:
                continue
            s = str(v).strip().lower()
            if not s:
                continue
            out.extend([p.strip() for p in s.split(",") if p.strip()])
        return out
    s = str(x).strip().lower()
    if not s:
        return []
    return [t.strip() for t in s.split(",") if t.strip()]


# =====================================================
# BMI
# =====================================================

def calc_bmi(weight_kg: float, height_cm: float) -> float:
    h_m = float(height_cm) / 100.0
    if h_m <= 0:
        return 0.0
    return float(weight_kg) / (h_m * h_m)


# =====================================================
# BMR (Mifflin–St Jeor)
# =====================================================

def calc_bmr_mifflin_st_jeor(
    age: int,
    gender: str,
    height_cm: float,
    weight_kg: float,
) -> float:
    """
    Mifflin–St Jeor BMR:
      Men:    10W + 6.25H - 5A + 5
      Women:  10W + 6.25H - 5A - 161
    """
    g = str(gender).lower().strip()
    base = 10.0 * float(weight_kg) + 6.25 * float(height_cm) - 5.0 * float(age)
    if g in {"female", "f", "woman", "women"}:
        return base - 161.0
    return base + 5.0


# =====================================================
# ACTIVITY MULTIPLIER
# =====================================================

def activity_multiplier(activity_level: str) -> float:
    a = str(activity_level).lower().strip()
    if a == "sedentary":
        return 1.2
    if a == "active":
        return 1.725
    return 1.55  # moderate default


# =====================================================
# TDEE
# =====================================================

def calc_tdee(user: Dict[str, Any]) -> float:
    bmr = calc_bmr_mifflin_st_jeor(
        age=int(user["age"]),
        gender=str(user.get("gender", "male")),
        height_cm=float(user["height_cm"]),
        weight_kg=float(user["weight_kg"]),
    )
    mult = activity_multiplier(user.get("activity_level", "moderate"))
    return float(bmr) * float(mult)


# =====================================================
# DAILY CALORIE TARGET
# =====================================================

def _clamp_calories(x: float, gender: str) -> int:
    g = str(gender).lower().strip()
    floor = 1200 if g in {"female", "f", "woman", "women"} else 1500
    ceiling = 4500
    x = float(x)
    x = max(float(floor), min(float(ceiling), x))
    return int(round(x))


def calc_daily_calorie_target(
    user: Dict[str, Any],
    final_goal: str,
    diabetes: bool = False,
) -> Dict[str, Any]:
    fg = str(final_goal).lower().strip()
    tdee = calc_tdee(user)
    dt = user.get("diet_type_user", "balanced")

    # Calories come from the weight goal only.
    if fg in {"weight_loss_balanced", "weight_loss_high_protein", "keto"}:
        target = tdee - 500.0
        method = "TDEE - 500 (fat loss)"
    elif fg in {"weight_gain_balanced", "weight_gain_high_protein"}:
        target = tdee + 350.0
        method = "TDEE + 350 (lean gain)"
    else:
        target = tdee
        method = "TDEE (maintenance)"

    gender = user.get("gender", "male")
    clamped_calories = _clamp_calories(target, gender)

    # Macro ratios. The diabetes flag overrides the diet's ratios (priority).
    if diabetes:
        p_ratio, c_ratio, f_ratio = 0.25, 0.40, 0.35
    elif dt == "keto":
        p_ratio, c_ratio, f_ratio = 0.25, 0.05, 0.70
    elif dt == "high_protein":
        p_ratio, c_ratio, f_ratio = 0.35, 0.35, 0.30
    else:  # balanced
        p_ratio, c_ratio, f_ratio = 0.20, 0.50, 0.30

    protein_g = (clamped_calories * p_ratio) / 4.0
    carbs_g = (clamped_calories * c_ratio) / 4.0
    fat_g = (clamped_calories * f_ratio) / 9.0

    bmr = calc_bmr_mifflin_st_jeor(
        age=int(user["age"]),
        gender=str(gender),
        height_cm=float(user["height_cm"]),
        weight_kg=float(user["weight_kg"]),
    )

    return {
        "bmr": float(bmr),
        "tdee": float(tdee),
        "target_calories": clamped_calories,
        "target_protein": round(protein_g, 1),
        "target_carbs": round(carbs_g, 1),
        "target_fat": round(fat_g, 1),
        "method": method,
    }


# =====================================================
# USER PROFILE BUILDER
# =====================================================

def build_user_profile(payload: Dict[str, Any]) -> Dict[str, Any]:
    age = int(payload["age"])
    height_cm = float(payload["height_cm"])
    weight_kg = float(payload["weight_kg"])

    gender = str(payload.get("gender", "male")).lower().strip()
    activity_level = str(payload.get("activity_level", "moderate")).lower().strip()

    if activity_level not in ACTIVITY_MAP:
        raise ValueError("activity_level must be: sedentary / moderate / active")

    diabetes = int(bool(payload.get("diabetes", False)))
    hypertension = int(bool(payload.get("hypertension", False)))
    dislikes = _normalize_list_like(payload.get("dislikes", []))
    allergies = _normalize_list_like(payload.get("allergies", []))

    general_goal_user = str(payload.get("general_goal", "auto")).lower().strip()

    diet_type_user = str(payload.get("diet_type", "balanced")).lower().strip().replace(" ", "_")
    if diet_type_user in ["high_protein", "protein", "hp"]:
        diet_type_user = "high_protein"
    elif diet_type_user in ["balanced", "mix", "normal"]:
        diet_type_user = "balanced"
    elif diet_type_user in ["keto", "low_carb"]:
        diet_type_user = "keto"
    else:
        diet_type_user = "balanced"

    cuisine_pref = str(payload.get("cuisine_pref", "any")).lower().strip()
    if cuisine_pref not in {"any", "egyptian", "arab", "egyptian_arab"}:
        cuisine_pref = "any"

    meals_per_day, snacks_per_day = clamp_meal_counts(
        payload.get("meals_per_day", 3), payload.get("snacks_per_day", 0)
    )

    return {
        "age": age,
        "gender": gender,
        "height_cm": height_cm,
        "weight_kg": weight_kg,
        "bmi": calc_bmi(weight_kg, height_cm),
        "activity_level": activity_level,
        "activity_encoded": ACTIVITY_MAP[activity_level],
        "diabetes": diabetes,
        "hypertension": hypertension,
        "dislikes": dislikes,
        "allergies": allergies,
        "general_goal_user": general_goal_user,
        "diet_type_user": diet_type_user,
        "cuisine_pref": cuisine_pref,
        "meals_per_day": meals_per_day,
        "snacks_per_day": snacks_per_day,
    }
