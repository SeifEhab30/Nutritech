from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Any
import re
import pandas as pd

from app.ai.gemini_helper import GeminiHelper

DATA_DIR = Path("data")
INDEX_PATH = DATA_DIR / "index.parquet"
SAMPLE_PATH = DATA_DIR / "sample.parquet"

gemini = GeminiHelper()

_index_df: pd.DataFrame | None = None
_sample_df: pd.DataFrame | None = None


def _load_data():
    global _index_df, _sample_df

    if _index_df is None:
        print("📦 Loading food index...")
        _index_df = pd.read_parquet(INDEX_PATH)

    if _sample_df is None:
        print("📦 Loading food sample...")
        _sample_df = pd.read_parquet(SAMPLE_PATH)


def _search_foods(query: str, limit: int = 8) -> List[Dict[str, Any]]:
    _load_data()
    assert _index_df is not None

    q = query.lower().strip()
    mask = _index_df["description_lc"].str.contains(re.escape(q), na=False)
    hits = _index_df.loc[mask].head(limit)

    foods = []
    for _, row in hits.iterrows():
        foods.append({
            "description": row["description"],
            "Calories": row["Calories"],
            "Protein": row["Protein"],
            "Carbs": row["Carbs"],
            "Fat": row["Fat"],
        })

    return foods


def ask_chatbot(message: str, history: List[Dict[str, str]] | None = None) -> str:
    foods = _search_foods(message)
    facts = {"foods_found": foods} if foods else None

    reply, ok = gemini.generate(
        user_message=message,
        facts=facts,
        history=history,
    )

    if ok and reply:
        return reply

    return "😢"