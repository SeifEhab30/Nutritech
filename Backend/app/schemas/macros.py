from pydantic import BaseModel, Field
from typing import Literal, Optional

class MacrosRequest(BaseModel):
    age: int = Field(..., ge=10, le=120)
    gender: Literal["male", "female"]
    height: float = Field(..., ge=80, le=250)      # cm
    weight: float = Field(..., ge=25, le=400)      # kg
    activityLevel: Literal["sedentary", "moderate", "active"]
    generalGoal: Literal[
        "weight_loss",
        "weight_gain",
        "maintain_weight"
    ]
    dietType: Optional[
        Literal["balanced", "high_protein", "keto"]
    ] = "balanced"
    # Health flag: overrides the diet macros when set.
    diabetes: Optional[bool] = False


class MacrosResponse(BaseModel):
    calories: int
    protein: int
    carbs: int
    fats: int
