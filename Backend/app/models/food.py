from sqlalchemy import Column, Integer, String, Float
from app.database import Base

class FoodItem(Base):
    __tablename__ = "food_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True)  # ✅ لازم طول

    serving_size_g = Column(Float)
    
    # Nutrition ranges
    calories_min = Column(Float)
    calories_max = Column(Float)
    protein_min = Column(Float)
    protein_max = Column(Float)
    carbs_min = Column(Float)
    carbs_max = Column(Float)
    fat_min = Column(Float)
    fat_max = Column(Float)
    fiber_min = Column(Float)
    fiber_max = Column(Float)