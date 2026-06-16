from pydantic import BaseModel
from typing import List, Dict, Optional

class NutritionRange(BaseModel):
    min: float
    max: float

class FoodNutrition(BaseModel):
    food_name: str
    serving_size_g: float
    count: int
    total_weight_g: float
    calories: NutritionRange
    protein: NutritionRange
    carbs: NutritionRange
    fat: NutritionRange
    fiber: NutritionRange

class DetectionResponse(BaseModel):
    detections: List[FoodNutrition]
    total_macros: Dict[str, NutritionRange]
    annotated_image: str
