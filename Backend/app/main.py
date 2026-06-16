from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.rate_limit import limiter
from app.routers import macros, auth, chat, profile, detection, plan, substitute, foods, tracker
from app.database import engine, Base
from app.routers import plan
from app.routers import substitute

# إنشاء الجداول تلقائياً
Base.metadata.create_all(bind=engine)

# Seed the image-recognition food_items table on first boot (no-op once seeded).
# nutritech.db is gitignored, so a fresh clone gets this reference data for free.
try:
    from seed_db import seed_food_if_empty
    seed_food_if_empty()
except Exception as e:
    print(f"WARNING: food_items auto-seed skipped: {e}")

app = FastAPI()

# Rate limiting (slowapi): register the limiter + the 429 handler.
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # أثناء التطوير فقط
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(macros.router)
app.include_router(chat.router)   # ضيف السطر ده
app.include_router(profile.router)
app.include_router(detection.router)

app.include_router(substitute.router)
app.include_router(plan.router)
app.include_router(foods.router)
app.include_router(tracker.router)
@app.get("/")
def root():
    return {"message": "Backend is running 🚀"}