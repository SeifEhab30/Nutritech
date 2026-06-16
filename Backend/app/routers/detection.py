from fastapi import APIRouter, UploadFile, File, Depends, Form, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.detection_service import detection_service
from app.core.rate_limit import limiter
from app.core.security import require_premium
from app.models.user import User
import json
from typing import Optional

router = APIRouter(prefix="/detection", tags=["Food Detection"])

# Upload guards
ALLOWED_IMAGE_TYPES = {
    "image/jpeg", "image/jpg", "image/png", "image/webp", "image/bmp",
}
MAX_IMAGE_BYTES = 10 * 1024 * 1024  # 10 MB


def _parse_weights(weights: Optional[str]) -> Optional[dict]:
    """Validate the optional weights JSON: a flat {food_name: positive_number} map."""
    if not weights:
        return None
    try:
        data = json.loads(weights)
    except (json.JSONDecodeError, TypeError):
        raise HTTPException(status_code=400, detail="weights must be valid JSON")
    if not isinstance(data, dict):
        raise HTTPException(status_code=400, detail="weights must be a JSON object")
    cleaned = {}
    for name, grams in data.items():
        if not isinstance(grams, (int, float)) or isinstance(grams, bool) or grams <= 0:
            raise HTTPException(
                status_code=400,
                detail=f"weight for '{name}' must be a positive number (grams)",
            )
        cleaned[str(name)] = float(grams)
    return cleaned or None


@router.post("/detect")
@limiter.limit("20/minute")
async def detect_food_endpoint(
    request: Request,
    image: UploadFile = File(...),
    weights: Optional[str] = Form(None, description='Optional JSON string for weights, e.g. {"burger": 250, "chicken": 500}'),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_premium),
):
    # --- validate the upload before doing any work ---
    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported image type '{image.content_type}'. "
                   "Allowed: JPEG, PNG, WEBP, BMP.",
        )
    # reject oversized files up front when the size is known (avoids buffering huge uploads)
    if image.size is not None and image.size > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="Image too large (max 10 MB).")

    user_weights = _parse_weights(weights)

    image_bytes = await image.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Empty image file.")
    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="Image too large (max 10 MB).")

    # Run the detection service
    try:
        result = detection_service.detect_food(db, image_bytes, user_weights=user_weights)
    except ValueError as e:
        # e.g. bytes that aren't a decodable image
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error in detection endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error processing detection")

    return result
