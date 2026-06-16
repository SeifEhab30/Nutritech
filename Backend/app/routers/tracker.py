# =====================================================
# NutriTech - Daily Intake Tracker
# Log foods eaten per day, compare against the profile's
# macro targets, and aggregate a date range for the
# progress dashboard.
# =====================================================

from datetime import date as date_cls, datetime, timedelta
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database import get_db
from app.models.daily_log import DailyLog
from app.models.user import User
from app.routers.profile import calculate_daily_needs
from app.schemas.tracker import DayResponse, LogEntryCreate

router = APIRouter(prefix="/tracker", tags=["Daily Tracker"])

_MACRO_FIELDS = ("calories", "protein", "carbs", "fat")


def _today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def _target_block(user: User) -> Optional[Dict[str, float]]:
    """Daily macro targets from the saved profile, or None if incomplete."""
    if not user.profile:
        return None
    try:
        return calculate_daily_needs(user.profile)
    except Exception:
        return None


def _day_response(db: Session, user: User, day: str) -> DayResponse:
    rows = (
        db.query(DailyLog)
        .filter(DailyLog.user_id == user.id, DailyLog.date == day)
        .order_by(DailyLog.id.asc())
        .all()
    )
    totals = {"calories": 0.0, "protein": 0.0, "carbs": 0.0, "fats": 0.0}
    for r in rows:
        totals["calories"] += r.calories or 0.0
        totals["protein"] += r.protein or 0.0
        totals["carbs"] += r.carbs or 0.0
        totals["fats"] += r.fat or 0.0
    totals = {k: round(v, 1) for k, v in totals.items()}

    return DayResponse(
        date=day,
        target=_target_block(user),
        totals=totals,
        entries=rows,
    )


@router.post("/log", response_model=DayResponse)
def add_log(
    body: LogEntryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DayResponse:
    day = body.date or _today()
    source = body.source if body.source in ("plan", "search", "manual") else "manual"
    entry = DailyLog(
        user_id=current_user.id,
        date=day,
        name=body.name,
        grams=body.grams,
        calories=round(body.calories, 1),
        protein=round(body.protein, 1),
        carbs=round(body.carbs, 1),
        fat=round(body.fat, 1),
        source=source,
    )
    db.add(entry)
    db.commit()
    return _day_response(db, current_user, day)


@router.get("/day", response_model=DayResponse)
def get_day(
    date: Optional[str] = Query(None, min_length=10, max_length=10),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DayResponse:
    return _day_response(db, current_user, date or _today())


@router.delete("/log/{entry_id}", response_model=DayResponse)
def delete_log(
    entry_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DayResponse:
    entry = (
        db.query(DailyLog)
        .filter(DailyLog.id == entry_id, DailyLog.user_id == current_user.id)
        .first()
    )
    if not entry:
        raise HTTPException(status_code=404, detail="Log entry not found")
    day = entry.date
    db.delete(entry)
    db.commit()
    return _day_response(db, current_user, day)


def _date_list(start: str, end: str) -> List[str]:
    """Inclusive 'YYYY-MM-DD' day list from start..end (capped at 92 days)."""
    s = date_cls.fromisoformat(start)
    e = date_cls.fromisoformat(end)
    if e < s:
        s, e = e, s
    span = min((e - s).days, 92)
    return [(s + timedelta(days=i)).isoformat() for i in range(span + 1)]


@router.get("/range")
def get_range(
    start: Optional[str] = Query(None, min_length=10, max_length=10),
    end: Optional[str] = Query(None, min_length=10, max_length=10),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict:
    end = end or _today()
    start = start or (date_cls.fromisoformat(end) - timedelta(days=6)).isoformat()
    try:
        days = _date_list(start, end)
    except ValueError:
        raise HTTPException(status_code=400, detail="Dates must be YYYY-MM-DD")

    # zero-filled per-day buckets, then fold in the logged rows
    buckets = {d: {"date": d, "calories": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0}
               for d in days}
    rows = (
        db.query(DailyLog)
        .filter(
            DailyLog.user_id == current_user.id,
            DailyLog.date >= days[0],
            DailyLog.date <= days[-1],
        )
        .all()
    )
    for r in rows:
        b = buckets.get(r.date)
        if b is None:
            continue
        for f in _MACRO_FIELDS:
            b[f] += getattr(r, f) or 0.0

    series = [
        {k: (round(v, 1) if isinstance(v, float) else v) for k, v in buckets[d].items()}
        for d in days
    ]
    return {"target": _target_block(current_user), "days": series}
