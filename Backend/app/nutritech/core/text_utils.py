# =====================================================
# NutriTech - Text Utilities
# Regex helpers, phrase matching, drop_words
# =====================================================

import re
from typing import Dict, List, Tuple

import pandas as pd

from app.nutritech.core.config import FINAL_HARD_NOT_MEAL_WORDS, MEAL_BAD_PAT

# =====================================================
# SAFER TEXT MATCHING
# =====================================================

def _phrase_to_regex(phrase: str) -> str:
    p = str(phrase).strip().lower()
    if not p:
        return ""
    tokens = [re.escape(t) for t in re.split(r"\s+", p) if t]
    if not tokens:
        return ""
    return r"(?<!\w)" + r"(?:\s+)".join(tokens) + r"(?!\w)"


def _build_words_regex(words: List[str]) -> str:
    parts = []
    for w in words:
        rx = _phrase_to_regex(w)
        if rx:
            parts.append(rx)
    if not parts:
        return ""
    return r"(?:%s)" % "|".join(parts)


_WORDS_REGEX_CACHE: Dict[Tuple[str, ...], re.Pattern] = {}


def _ensure_display_name(df: pd.DataFrame) -> pd.DataFrame:
    if "display_name" not in df.columns and "description" in df.columns:
        out = df.copy()
        out["display_name"] = out["description"].astype(str)
        return out
    return df


def drop_words(df: pd.DataFrame, words: List[str]) -> pd.DataFrame:
    if df is None or df.empty or not words:
        return df
    df = _ensure_display_name(df)
    key = tuple(sorted({str(w).strip().lower() for w in words if str(w).strip()}))
    if not key:
        return df
    if key not in _WORDS_REGEX_CACHE:
        pat = _build_words_regex(list(key))
        if not pat:
            return df
        _WORDS_REGEX_CACHE[key] = re.compile(pat, flags=re.IGNORECASE)
    rx = _WORDS_REGEX_CACHE[key]
    s = df["display_name"].astype(str).str.lower()
    return df[~s.str.contains(rx, na=False, regex=True)].copy()


def conditional_drop_words(
    df: pd.DataFrame,
    words: List[str],
    *,
    min_rows_before: int = 250,
    min_keep_fraction: float = 0.65,
) -> pd.DataFrame:
    if df is None or df.empty or not words:
        return df
    if df.shape[0] < int(min_rows_before):
        return df
    before = df.shape[0]
    out = drop_words(df, words)
    if out.shape[0] < int(before * float(min_keep_fraction)):
        return df
    return out


# =====================================================
# FINAL "REAL MEAL" GATE
# =====================================================

def final_hard_meal_filter(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    out = drop_words(out, FINAL_HARD_NOT_MEAL_WORDS)
    out = out[~out["display_name"].astype(str).str.contains(MEAL_BAD_PAT, na=False)].copy()
    return out


# =====================================================
# NAME CANONICALIZATION
# =====================================================

BRAND_NOISE = {
    "gefen", "kirkland", "trader", "joe", "costco", "aldi", "walmart", "target",
    "sweet", "earth", "mindful", "craveables", "craveable",
    "advancepierre", "ahold", "amy", "armour",
}

STOPWORDS = {
    "a", "an", "the", "and", "or", "of", "with", "in", "on", "for",
    "style", "original", "classic", "premium", "natural", "organic",
    "fully", "cooked", "uncooked", "rte", "ready", "to", "eat",
    "oz", "lb", "ct", "pack", "pcs", "pc", "count",
}

DISH_WORDS = {
    "hummus", "dip", "spread", "ravioli", "panini", "club",
    "tamale", "pizza", "burrito", "sandwich", "wrap",
}

SYNONYMS = {
    "chickpeas": "chickpea", "garbanzo": "chickpea", "garbanzos": "chickpea",
    "gram": "chickpea", "chana": "chickpea", "beans": "bean",
    "breasts": "breast", "tenderloins": "tenderloin", "tenders": "tender",
}


def _tokenize(text: str) -> List[str]:
    s = str(text).lower().strip()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s.split()


def _singularize(w: str) -> str:
    if w.endswith("ies") and len(w) > 4:
        return w[:-3] + "y"
    if w.endswith("s") and len(w) > 3 and not w.endswith("ss"):
        return w[:-1]
    return w


def normalize_tokens(tokens: List[str]) -> List[str]:
    out: List[str] = []
    for w in tokens:
        w = _singularize(w)
        w = SYNONYMS.get(w, w)
        if w.isdigit():
            continue
        if w in STOPWORDS:
            continue
        if w in BRAND_NOISE:
            continue
        out.append(w)
    return out


def simplify_food_name(name: str) -> str:
    s = str(name).lower().strip()
    s = re.sub(r"^[\d\.\-/\s]*(?:oz|lb|ct|pc|pcs|#)?\s*", "", s)
    s = re.sub(r"[^a-z\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s.title() if s else "Unknown"


def canonical_name(display_name: str) -> str:
    toks = normalize_tokens(_tokenize(display_name))

    if any(w in DISH_WORDS for w in toks):
        key = toks[:3]
        return " ".join(key).title() if key else "Unknown"

    if "chickpea" in toks:
        if "bean" in toks:
            return "Chickpea Bean"
        return "Chickpea"

    if "chicken" in toks:
        if "breast" in toks:
            return "Chicken Breast"
        if "tenderloin" in toks:
            return "Chicken Tenderloin"
        if "tender" in toks:
            return "Chicken Tender"
        return "Chicken"

    key = toks[:3]
    return " ".join(key).title() if key else "Unknown"


def strong_key(canonical: str) -> str:
    toks = normalize_tokens(_tokenize(canonical))
    key = toks[:2]
    return " ".join(key).title() if key else "Unknown"
