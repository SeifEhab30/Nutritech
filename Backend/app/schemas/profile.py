from pydantic import BaseModel, Field
from typing import List, Optional, Union


# =========================
# Base Schema
# =========================
# Fields stay Optional (partial updates) but are bounds-checked when present,
# so age=-5 / weight=0 can't silently corrupt the BMR/TDEE math.

class UserProfileBase(BaseModel):
    age: Optional[int] = Field(None, ge=10, le=120)
    gender: Optional[str] = None
    height: Optional[float] = Field(None, ge=80, le=250)      # cm
    weight: Optional[float] = Field(None, ge=25, le=400)      # kg
    activity_level: Optional[str] = None
    general_goal: Optional[str] = None
    diet_type: Optional[str] = None

    # Health flags + preferences
    diabetes: Optional[bool] = None
    hypertension: Optional[bool] = None
    cuisine_pref: Optional[str] = None
    # Accept either a list (UI checklist) or a comma string; persisted as a string.
    dislikes: Optional[Union[List[str], str]] = None
    allergies: Optional[Union[List[str], str]] = None


# =========================
# Create / Update
# =========================

class UserProfileCreate(UserProfileBase):
    pass


class UserProfileUpdate(UserProfileBase):
    pass


# =========================
# Response Schema
# =========================

class UserProfile(UserProfileBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True


# =========================
# Daily Needs Schema
# =========================

class DailyNeeds(BaseModel):
    calories: float
    protein: float
    carbs: float
    fats: float


class ProfileWithNeeds(BaseModel):
    profile: UserProfile
    daily_needs: DailyNeeds