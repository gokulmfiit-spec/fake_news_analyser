# VerifyNews — Fake News Detection Platform

A full-stack web application for verifying the authenticity of news articles, headlines, social
media posts, and URLs using NLP/ML and an optional LLM API, with source credibility analysis and
a reports/analytics dashboard.

**Stack:** React.js · Django REST Framework · SQLite (dev) / PostgreSQL or MySQL (prod) · JWT auth

---

## Project Structure

```
fake-news-detection/
├── backend/                Django REST API
│   ├── config/              settings, root urls
│   ├── accounts/            Module: User Login & Registration
│   ├── submissions/         Module: News Article Submission + URL Verification
│   ├── ai_engine/           Module: AI Fake News Detection + Source Credibility Analysis
│   ├── reports/             Module: Fact Verification Report
│   ├── feedback/            Module: User Feedback
│   ├── analytics/           Module: Reports & Analytics Dashboard
│   ├── admin_panel/         Module: Admin Dashboard
│   └── common/               shared permissions
├── frontend/                React + Vite SPA
│   └── src/
│       ├── api/              axios client (JWT + auto-refresh)
│       ├── context/          auth context
│       ├── components/       Navbar, route guards, badges
│       └── pages/            Login, Register, Submit, ReportDetail, History, Analytics, Admin
├── postman/                  Postman collection covering every endpoint
└── docs/                     project plan / weekly review template
```

---

## 1. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env            # then edit .env (see below)

python manage.py migrate
python manage.py createsuperuser   # creates an admin account

python manage.py runserver
```

The API will be live at `http://127.0.0.1:8000/api/`. The Django admin is at
`http://127.0.0.1:8000/admin/`.

### `.env` configuration

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Django secret key — set a real random value for anything beyond local dev |
| `DB_ENGINE` | `sqlite` (default, zero-config) or `postgres` |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | Only used when `DB_ENGINE=postgres` (works for MySQL too if you swap the engine/driver) |
| `CORS_ALLOWED_ORIGINS` | Must include your frontend's origin, e.g. `http://localhost:5173` |
| `LLM_API_KEY` | Optional. Leave blank and the AI pipeline still works using the built-in ML/heuristic classifier — you just won't get LLM-generated verdicts/summaries |
| `LLM_API_URL`, `LLM_MODEL` | Defaults target the Anthropic Messages API; point at any compatible endpoint |
| `TRUSTED_NEWS_API_KEY` | Optional (e.g. NewsAPI.org key) — enables "related coverage from trusted sources" in reports |

### Switching to PostgreSQL or MySQL

Set `DB_ENGINE=postgres` and fill in the DB_* fields, then re-run `migrate`. For MySQL, install
`mysqlclient` instead of `psycopg2-binary` and change `ENGINE` in `config/settings.py` to
`django.db.backends.mysql`.

### Upgrading the AI classifier from heuristic → trained ML model

Out of the box, `ai_engine` uses a transparent rule-based heuristic classifier (clickbait
phrasing, sensational language, excessive punctuation, etc.) so the whole pipeline works with
zero setup. To swap in a real trained model:

```bash
# CSV must have `text` and `label` columns (label: real/fake)
python ai_engine/train_baseline.py path/to/dataset.csv
```

This trains a TF-IDF + Logistic Regression model and saves it to
`ai_engine/trained_model.joblib`. `classifier.py` automatically loads it on the next server
restart, no code changes needed. Good datasets to try: Kaggle's "Fake and Real News Dataset", or
the LIAR dataset reshaped to two columns.

---

## 2. Frontend Setup

```bash
cd frontend
npm install

cp .env.example .env    # points VITE_API_BASE_URL at your backend

npm run dev
```

The app runs at `http://localhost:5173`.

---

## 3. Running Both Together

Open two terminals:

```bash
# Terminal 1
cd backend && source venv/bin/activate && python manage.py runserver

# Terminal 2
cd frontend && npm run dev
```

Then visit `http://localhost:5173`, register an account, and submit an article or URL.

To access the Admin Dashboard in the UI, either promote your user via
`python manage.py createsuperuser`, or log in as an existing user and have an admin
promote you via `PATCH /api/admin-panel/users/<id>/` with `{"role": "admin"}`.

---

## 4. API Testing (Postman)

Import `postman/FakeNewsDetection.postman_collection.json` into Postman. It includes every
endpoint across all modules, using `{{base_url}}`, `{{access_token}}`, and `{{refresh_token}}`
collection variables — run **Login** first and copy the returned tokens into the collection
variables (or wire up a Postman test script to do it automatically).

---

## 5. Module ↔ Code Map

| Module | Backend | Frontend |
|---|---|---|
| User Login & Registration | `accounts/` | `pages/Login.jsx`, `pages/Register.jsx` |
| Admin Dashboard | `admin_panel/` | `pages/AdminDashboard.jsx` |
| News Article Submission | `submissions/` (`SubmitTextView`) | `pages/Submit.jsx` |
| URL Verification | `submissions/` (`SubmitURLView`, `scraper.py`) | `pages/Submit.jsx` |
| AI Fake News Detection | `ai_engine/` (`pipeline.py`, `classifier.py`, `llm_client.py`) | `pages/ReportDetail.jsx` |
| Source Credibility Analysis | `ai_engine/credibility.py` | `pages/ReportDetail.jsx` |
| Fact Verification Report | `reports/` | `pages/ReportDetail.jsx` |
| News Search and History | `submissions/` (`SubmissionHistoryView`) | `pages/History.jsx` |
| User Feedback | `feedback/` | `pages/ReportDetail.jsx` (feedback card) |
| Reports & Analytics Dashboard | `analytics/` | `pages/Analytics.jsx` |

---

## 6. What's Implemented vs. Stretch Goals

**Fully implemented and tested end-to-end:**
JWT auth, article/headline/social-post submission, URL scraping + verification, hybrid AI
pipeline (heuristic/ML classifier + optional LLM verdict, blended into one confidence score),
source credibility scoring, fact verification reports, search/history/filtering, feedback
capture, analytics dashboard (personal + platform-wide for admins), admin user management and
moderation feed.

**Stretch / optional (scaffolded, needs a live API key or dataset to fully activate):**
- **LLM API integration** — code is complete in `ai_engine/llm_client.py`; add `LLM_API_KEY` to
  `.env` to activate. Without it, the system still returns a full report using ML + heuristics.
- **Trusted News API cross-checking** — complete in `ai_engine/credibility.py`; add
  `TRUSTED_NEWS_API_KEY` to activate "related coverage" in reports.
- **RAG-based fact verification** — not built; the current design (LLM + credibility + optional
  trusted-news cross-check) covers the same goal more simply. If you need true RAG (embedding a
  trusted-source corpus and retrieving passages before the LLM call), the natural place to add it
  is inside `ai_engine/pipeline.py`, feeding retrieved passages into the LLM prompt in
  `llm_client.py`.

See `docs/project-plan.md` for the fuller build roadmap and weekly review template.

---

## 7. Deployment Notes (brief)

- Backend: set `DEBUG=False`, a real `SECRET_KEY`, proper `ALLOWED_HOSTS`, switch to Postgres/MySQL,
  serve via gunicorn + nginx (or a PaaS like Render/Railway).
- Frontend: `npm run build` produces `frontend/dist/` — serve as static files (Netlify, Vercel,
  nginx) and point `VITE_API_BASE_URL` at your deployed backend.
- Remember to update `CORS_ALLOWED_ORIGINS` on the backend to your deployed frontend URL.
