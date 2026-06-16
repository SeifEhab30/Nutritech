import pandas as pd
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.food import FoodItem
from app.models import food as food_model
import os

# Absolute so it resolves no matter the working directory (e.g. uvicorn startup).
EXCEL_PATH = os.path.join(os.path.dirname(__file__), "app", "dataused", "Food_Macros.xlsx")

def seed_food_data():
    if not os.path.exists(EXCEL_PATH):
        print(f"Error: Excel file not found at {EXCEL_PATH}")
        return

    print(f"Reading data from {EXCEL_PATH}...")
    try:
        # Based on Detectortesting.py, it skips the first descriptive header row
        df = pd.read_excel(EXCEL_PATH, skiprows=1)
        
        db = SessionLocal()
        try:
            # Clear existing data so the database perfectly matches the Excel file
            print("Clearing old database entries to match Excel...")
            db.query(FoodItem).delete()
            
            count = 0
            for _, row in df.iterrows():
                if pd.isna(row['Food Item']):
                    continue
                
                name = str(row['Food Item']).lower().strip()
                
                # Check if already exists
                existing_item = db.query(FoodItem).filter(FoodItem.name == name).first()
                
                food_data = {
                    "name": name,
                    "serving_size_g": row['Serving Size (g)'],
                    "calories_min": row['Min'],
                    "calories_max": row['Max'],
                    "protein_min": row['Min.1'],
                    "protein_max": row['Max.1'],
                    "carbs_min": row['Min.2'],
                    "carbs_max": row['Max.2'],
                    "fat_min": row['Min.3'],
                    "fat_max": row['Max.3'],
                }

                if existing_item:
                    for key, value in food_data.items():
                        setattr(existing_item, key, value)
                else:
                    new_item = FoodItem(**food_data)
                    db.add(new_item)
                
                count += 1
            
            db.commit()
            print(f"Successfully synced {count} food items to the database.")
        except Exception as e:
            db.rollback()
            print(f"Error during database sync: {e}")
        finally:
            db.close()
            
    except Exception as e:
        print(f"Error reading Excel file: {e}")

def seed_food_if_empty():
    """Populate food_items from the Excel source only when the table is empty.
    Safe to call on every startup — a no-op once seeded (so a fresh clone, whose
    nutritech.db is gitignored, gets the image-recognition reference data without
    a manual step)."""
    food_model.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(FoodItem).count() > 0:
            return
    finally:
        db.close()
    print("food_items table empty — seeding from Excel…")
    seed_food_data()


if __name__ == "__main__":
    # Ensure tables are created
    food_model.Base.metadata.create_all(bind=engine)
    seed_food_data()
