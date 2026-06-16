# NutriTech — Setup & Run Guide

Step-by-step instructions to run the project locally. You'll run **two terminals**
side by side: one for the backend, one for the frontend. Both must stay running
while you use the app.

---

## Prerequisites (install once)

- **Python 3.10+** (3.11 recommended) — check: `python --version`
- **Node.js 16+** and **npm** — check: `node --version`
- **Git** — check: `git --version`
- The **`.env` file** with the secret keys (sent to you separately — it is **not** in the repo)

---

## Step 1 — Clone the repo

```bash
git clone https://github.com/SeifEhab30/Nutritech.git
cd Nutritech
```

---

## Step 2 — Backend setup (Terminal 1)

```bash
cd Backend

# create a virtual environment
python -m venv venv
```

Activate it (pick your OS):

```bash
venv\Scripts\activate          # Windows (PowerShell or CMD)
source venv/bin/activate       # macOS / Linux
```

Install dependencies (this is a **large download** — torch / YOLO take a few
minutes; be patient):

```bash
pip install -r requirements.txt
```

---

## Step 3 — Add the `.env` file

Place the `.env` file inside the **`Backend/` folder** (same level as
`requirements.txt`). If you only have the template, copy it first:

```bash
copy .env.example .env         # Windows
cp .env.example .env           # macOS / Linux
```

Then open `Backend/.env` and fill in at minimum:

```
GEMINI_API_KEY=<the shared key>
JWT_SECRET_KEY=<any long random string>
```

Generate a strong `JWT_SECRET_KEY` with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Optional keys: `GEMINI_API_KEYS` (comma-separated backup keys for auto-rotation),
`USDA_API_KEY` (food search; falls back to a demo key).

---

## Step 4 — Run the backend (keep this terminal open)

```bash
uvicorn app.main:app --reload
```

✅ Backend runs at **http://127.0.0.1:8000** (API docs at
**http://127.0.0.1:8000/docs**). The database and AI model ship with the repo, and
the food table auto-seeds on first boot — no extra data setup needed.

---

## Step 5 — Frontend setup (Terminal 2 — a **new** terminal)

```bash
cd Nutritech/frontend
npm install
```

---

## Step 6 — Run the frontend

```bash
npm start
```

✅ Frontend opens at **http://localhost:3000**.

---

## Step 7 — Use the app

1. Click **Register** and create an account (password needs upper + lower + digit +
   symbol, 8+ characters).
2. Log in and fill out your **Profile** (required for the meal planner and macros).
3. Explore the free features. **Chatbot, Image Recognition, and Weekly Plans are
   Premium** — a new account is Free, so go to **Get Premium → Subscribe** (a free
   mock toggle) to unlock them.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `uvicorn: command not found` | The venv isn't activated — re-run the activate command from Step 2. |
| Chatbot returns an error | `.env` is missing `GEMINI_API_KEY`, or `.env` isn't in the `Backend/` folder. |
| Logged out after every backend restart | `JWT_SECRET_KEY` isn't set in `.env` (a temporary key is used otherwise). |
| Frontend loads but every action fails | Make sure the **backend terminal is still running** on port 8000. |
| `pip install` looks stuck | It's downloading torch (~hundreds of MB). Let it finish. |

> **Both terminals must stay running** the whole time you use the app — one for the
> backend (port 8000), one for the frontend (port 3000).
