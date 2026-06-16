from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.macros import MacrosRequest, MacrosResponse
from app.services.macros_service import calculate_macros

from app.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.macros_history import MacrosHistory

router = APIRouter(prefix="/macros", tags=["Macros"])


@router.post("/calculate", response_model=MacrosResponse)
def calculate(
    data: MacrosRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1️⃣ نحسب الماكروز
    result = calculate_macros(data)

    # 2️⃣ نحفظ النتيجة في database
    history = MacrosHistory(
        user_id=current_user.id,
        calories=result["calories"],
        protein=result["protein"],
        carbs=result["carbs"],
        fats=result["fats"],
    )

    db.add(history)
    db.commit()

    # 3️⃣ نرجع النتيجة للفرونت
    return result