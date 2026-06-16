from typing import List, Optional

from pydantic import BaseModel, Field


# What sources the UI may attribute an entry to.
_SOURCES = ("plan", "search", "manual")


class LogEntryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    calories: float = Field(0.0, ge=0)
    protein: float = Field(0.0, ge=0)
    carbs: float = Field(0.0, ge=0)
    fat: float = Field(0.0, ge=0)
    grams: Optional[float] = Field(None, ge=0)
    source: str = "manual"
    # 'YYYY-MM-DD'; defaults to today (server-local) when omitted.
    date: Optional[str] = Field(None, min_length=10, max_length=10)


class LogEntryOut(BaseModel):
    id: int
    date: str
    name: str
    grams: Optional[float] = None
    calories: float
    protein: float
    carbs: float
    fat: float
    source: str

    class Config:
        from_attributes = True


class MacroBlock(BaseModel):
    calories: float = 0.0
    protein: float = 0.0
    carbs: float = 0.0
    fats: float = 0.0


class DayResponse(BaseModel):
    date: str
    target: Optional[MacroBlock] = None  # None when the profile is incomplete
    totals: MacroBlock
    entries: List[LogEntryOut]


class RangeDay(BaseModel):
    date: str
    calories: float = 0.0
    protein: float = 0.0
    carbs: float = 0.0
    fat: float = 0.0


class RangeResponse(BaseModel):
    target: Optional[MacroBlock] = None
    days: List[RangeDay]
