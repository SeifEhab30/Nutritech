# =====================================================
# NutriTech - Goal Engine (rule-based)
# Determines the user's general goal, then maps
# (general goal x diet type) -> one of 7 final goals.
#
# Goals are weight objectives only: weight_loss / weight_gain /
# maintain_weight. Diabetes and hypertension are health *flags*
# (handled in scoring + macro targets), not goals.
#
# Note: the previous Decision Tree was trained on 12
# synthetic rows (not real ML). This rule engine is the
# honest "Rule-Based Decision Engine" from Seminar 2.
# =====================================================

from typing import Any, Dict


# =====================================================
# GENERAL GOAL  (rule-based on BMI)
# =====================================================

def predict_general_goal(user: Dict[str, Any]) -> str:
    """Infer the weight goal when the user selects 'auto'."""
    bmi = float(user.get("bmi", 0.0))

    if bmi <= 0:
        return "maintain_weight"
    if bmi < 18.5:
        return "weight_gain"
    if bmi >= 25.0:
        return "weight_loss"
    return "maintain_weight"


# =====================================================
# GOAL MAPPING  (general goal x diet type -> final goal)
# =====================================================

def map_to_final_goal(general_goal: str, diet_type: str) -> str:
    general_goal = str(general_goal).lower().strip()
    diet_type = str(diet_type).lower().strip()

    # Accept frontend/profile aliases for the canonical goals.
    aliases = {
        "muscle_gain": "weight_gain",
        "gain_weight": "weight_gain",
        "lose_weight": "weight_loss",
        "maintenance": "maintain_weight",
    }
    general_goal = aliases.get(general_goal, general_goal)

    if general_goal == "weight_loss":
        if diet_type == "high_protein":
            return "weight_loss_high_protein"
        if diet_type == "keto":
            return "keto"
        return "weight_loss_balanced"

    if general_goal == "weight_gain":
        if diet_type == "high_protein":
            return "weight_gain_high_protein"
        return "weight_gain_balanced"

    if general_goal in ("maintain_weight", "maintenance"):
        if diet_type == "high_protein":
            return "maintenance_high_protein"
        return "maintenance_balanced"

    return "maintenance_balanced"
