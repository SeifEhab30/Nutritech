# NutriTech 🥗

An AI-powered nutrition web app: **FastAPI** backend + **React** frontend.
It combines food **image recognition** (YOLOv8), an **AI nutrition chatbot**
(Google Gemini, RAG-backed), a personalized **meal planner** (K-Means + KNN),
**macro calculation**, **food search**, and a **daily/weekly nutrition tracker** —
with **Free / Premium** account tiers.

> 🚀 **Just want to run it?** See **[SETUP.md](SETUP.md)** for the full step-by-step guide.

---

## ✨ Features

| Feature | Description | Tier |
|---|---|---|
| Macros Calculator | BMR/TDEE + macro targets from your profile | Free |
| Food Search | Look up any food's macros (USDA + curated dataset) | Free |
| Daily Meal Plan | Personalized daily plan, dynamic meals (2–6) + snacks (0–4) | Free |
| Profile & Tracker | 4-tab profile, daily macro logging, progress dashboard | Free |
| **AI Chatbot** | Gemini-powered nutrition assistant with conversation memory | **Premium** |
| **Image Recognition** | Detect food from a photo and estimate its macros | **Premium** |
| **Weekly Meal Plans** | Full 7-day plan generation | **Premium** |

Premium gating is enforced on the **backend** (403 for free users) and reflected
in the **UI** (locked-feature overlay → `/pricing`). Subscription is a mock
toggle (no real payment).

---

## 🧱 Tech Stack

- **Backend:** FastAPI, SQLAlchemy, SQLite, JWT auth (python-jose), bcrypt, slowapi (rate limiting)
- **AI/ML:** Ultralytics YOLOv8 (detection), Google Gemini (chatbot), scikit-learn (K-Means clustering + KNN), pandas
- **Frontend:** React (CRA), React Router, Recharts

---

## 📁 Project Structure

```
Backend/
  app/
    main.py            # FastAPI app, router wiring, startup seeding
    database.py        # SQLite engine/session
    routers/           # auth, profile, macros, plan, detection, chat, foods, tracker, substitute
    models/ schemas/   # SQLAlchemy models + Pydantic schemas
    services/          # detection_service, macros_service
    ai/                # gemini_helper, rag_service
    nutritech/         # meal-planner engine (data_loader, planner, scoring, knn_substitute)
    AI_Models/best.pt  # YOLOv8 weights
    dataused/          # Food_Macros.xlsx (seed source for image-recognition food table)
  data/                # foods_curated.csv (planner), index/sample.parquet (RAG index)
  seed_db.py           # seeds food_items from Excel (auto-runs on startup if empty)
  requirements.txt
  nutritech.db         # SQLite DB (committed, with seed data)
frontend/
  src/                 # components, api clients, styles
  public/
```

---

## 🚀 Getting Started

### Prerequisites
- **Python 3.11** (3.10+ should work)
- **Node.js 16+** and **npm**

### 1. Backend (FastAPI)

```bash
cd Backend

# create + activate a virtual environment
python -m venv venv
venv\Scripts\activate           # Windows
# source venv/bin/activate      # macOS/Linux

# install dependencies
pip install -r requirements.txt

# set up environment variables
copy .env.example .env          # Windows  (cp on macOS/Linux)
# then edit .env and fill in your keys (see below)

# run the server
uvicorn app.main:app --reload
```

Backend runs at `http://127.0.0.1:8000` — interactive docs at `/docs`.

On startup the app auto-creates any missing tables and seeds the
image-recognition food table from `app/dataused/Food_Macros.xlsx` if it's empty.

### 2. Frontend (React)

```bash
cd frontend
npm install
npm start
```

Frontend runs at `http://localhost:3000`.

---

## 🔑 Environment Variables (`Backend/.env`)

Copy `Backend/.env.example` → `Backend/.env` and fill in:

| Variable | Required | Purpose |
|---|---|---|
| `GEMINI_API_KEY` | Yes (for chatbot) | Google Gemini API key |
| `JWT_SECRET_KEY` | Yes | Secret for signing JWT auth tokens |
| `GEMINI_API_KEYS` | Optional | Comma-separated backup Gemini keys; auto-rotates on quota/429 |
| `USDA_API_KEY` | Optional | USDA FoodData Central key for Food Search (falls back to `DEMO_KEY`) |

> ⚠️ `.env` is gitignored — never commit your real keys. Generate a strong
> `JWT_SECRET_KEY`, e.g. `python -c "import secrets; print(secrets.token_urlsafe(48))"`.

---

## 🗄️ Database

SQLite (`Backend/nutritech.db`) is committed with seed data. Tables:
`users`, `user_profiles`, `daily_logs`, `saved_plans`, `macros_history`,
`food_items`. Missing tables are created automatically on startup.

---

## 👥 Notes

- Pull the latest changes before starting work.
- Never commit your `.env` (use `.env.example` as the template).
- After changing backend Python, restart `uvicorn` (or run with `--reload`).
