# =====================================================
# NutriTech v2 - Food Data Loader
# Loads the curated everyday-foods dataset ONCE, derives
# macro ratios, fits K-Means clusters (variety) and a KNN
# index (substitution). Cached as a process singleton.
# =====================================================

from typing import Optional

import numpy as np
import pandas as pd
from sklearn.cluster import MiniBatchKMeans
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

from app.nutritech.core.config import (
    CLUSTER_FEATURES,
    DATA_PATH,
    MACRO_COLS,
    N_CLUSTERS,
    NUTRIENT_FEATURES,
)


# =====================================================
# PREPARE
# =====================================================

def prepare(df: pd.DataFrame) -> pd.DataFrame:
    """Coerce numerics, derive macro-energy ratios, normalize text cols."""
    d = df.copy()

    for c in MACRO_COLS:
        if c not in d.columns:
            d[c] = 0.0
        d[c] = pd.to_numeric(d[c], errors="coerce").fillna(0.0).clip(lower=0.0)

    d["serving_g"] = pd.to_numeric(d.get("serving_g", 100.0), errors="coerce").fillna(100.0)

    cal = d["kcal_100g"].replace(0, np.nan)
    d["protein_ratio"] = (4.0 * d["protein_100g"] / cal).fillna(0.0).clip(0.0, 1.6)
    d["carb_ratio"] = (4.0 * d["carbs_100g"] / cal).fillna(0.0).clip(0.0, 1.6)
    d["fat_ratio"] = (9.0 * d["fat_100g"] / cal).fillna(0.0).clip(0.0, 1.6)

    for c, default in [("name", ""), ("role", "side"), ("cuisine", "intl"),
                       ("diet_tags", "balanced"), ("item_kind", "component")]:
        if c not in d.columns:
            d[c] = default
        d[c] = d[c].fillna(default).astype(str)

    d = d[d["kcal_100g"] > 0].reset_index(drop=True)
    return d


# =====================================================
# MODELS
# =====================================================

def fit_clusters(d: pd.DataFrame):
    X = d[CLUSTER_FEATURES].to_numpy(dtype=float)
    scaler = StandardScaler().fit(X)
    k = int(min(N_CLUSTERS, len(d)))
    km = MiniBatchKMeans(n_clusters=k, random_state=42, n_init=10, batch_size=256)
    km.fit(scaler.transform(X))
    return scaler, km


def fit_knn(d: pd.DataFrame):
    X = d[NUTRIENT_FEATURES].to_numpy(dtype=float)
    scaler = StandardScaler().fit(X)
    knn = NearestNeighbors(n_neighbors=int(min(20, len(d))), metric="euclidean")
    knn.fit(scaler.transform(X))
    return scaler, knn


# =====================================================
# STORE
# =====================================================

class FoodStore:
    def __init__(self, df: pd.DataFrame):
        self.df = prepare(df)
        self.cluster_scaler, self.kmeans = fit_clusters(self.df)
        self.df["cluster"] = self.kmeans.labels_
        self.knn_scaler, self.knn = fit_knn(self.df)


_STORE: Optional[FoodStore] = None


def get_food_store(df: Optional[pd.DataFrame] = None) -> FoodStore:
    """Return the cached FoodStore, building it once from DATA_PATH (or a df)."""
    global _STORE
    if _STORE is None:
        if df is None:
            df = pd.read_csv(DATA_PATH, low_memory=False)
        _STORE = FoodStore(df)
    return _STORE
