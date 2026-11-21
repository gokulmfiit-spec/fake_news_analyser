# Fake News Detection Platform — Project Plan

**Deadline:** 15.08.2026
**Plan date:** 02.08.2026
**Duration available:** 13 days ⚠️ (see Feasibility Note below)

---

## 0. Feasibility Note (read first)

The requested scope — 10 modules, JWT auth, admin dashboard, ML/NLP fake-news classifier, LLM-based fact verification, RAG over trusted sources, analytics dashboard, full React + Django REST stack — is a **6–10 week** build for a student team under normal weekly-review pacing. In 13 days it is only achievable if:

1. The AI model is a **pretrained/fine-tuned classifier** (e.g. a HuggingFace fake-news dataset model) rather than trained from scratch, and
2. RAG and Trusted News API integration are treated as **stretch goals**, not core deliverables, and
3. The team works in parallel tracks (backend/AI vs frontend) from day one.

If the 15.08.2026 date is fixed and non-negotiable, use the **13-Day Sprint Plan (Section 4)**. If there's flexibility, use the **7-Week Plan (Section 5)**, which matches a normal weekly-review cadence and is what I'd recommend for genuine learning outcomes given the stated goal of understanding "the complete workflow."

---

## 1. System Architecture

```
┌─────────────────────┐        ┌──────────────────────────┐        ┌─────────────────┐
│   React.js Frontend  │  REST  │   Django REST Framework   │  ORM   │  PostgreSQL /    │
│  (Vite/CRA, Axios,   │◄──────►│   (JWT auth, viewsets,     │◄──────►│  MySQL           │
│   React Router)      │  JSON  │   serializers, permissions)│        │                  │
└─────────────────────┘        └───────────┬──────────────┘        └─────────────────┘
                                            │
                              ┌─────────────┴─────────────┐
                              │        AI Service Layer     │
                              │  (Django app or FastAPI      │
                              │   microservice)              │
                              │  - NLP preprocessing         │
                              │  - ML classifier (sklearn/    │
                              │    HF transformers)          │
                              │  - LLM API call (fact check, │
                              │    summary, RAG)             │
                              │  - Source credibility scorer │
                              └─────────────┬─────────────┘
                                            │
                              ┌─────────────┴─────────────┐
                              │  External APIs (optional)   │
                              │  - Trusted News API          │
                              │  - Search/RAG source store    │
                              └───────────────────────────┘
```

**Key design decisions:**
- Keep the AI logic as a **separate Django app** (`ai_engine`) with a clean internal API (`analyze(text) -> {label, confidence, flagged_statements, sources, summary}`), so it can later be split into a microservice without touching the rest of the backend.
- Use **JWT** via `djangorestframework-simplejwt`.
- Store submissions, verification results, and feedback in normalized tables so the History and Analytics modules can query directly rather than recomputing.

---

## 2. Module Breakdown

| # | Module | Core Django apps/models | Core React views | Notes |
|---|--------|--------------------------|-------------------|-------|
| 1 | User Login & Registration | `accounts` (User, Profile) | Login, Register, Profile | JWT access+refresh tokens, password hashing via Django default |
| 2 | Admin Dashboard | Django admin + custom `admin_panel` app | AdminHome, UserManagement, ContentModeration | Role field on User (`is_admin`); restrict via DRF permission classes |
| 3 | News Article Submission | `submissions` (Submission model) | SubmitArticle form | Text/paste input, stores raw content + metadata |
| 4 | URL Verification | `submissions` (extended) | SubmitURL form | Scrape via `requests`+`BeautifulSoup`, extract title/body before analysis |
| 5 | AI Fake News Detection | `ai_engine` | ResultView (shows label + confidence) | ML model + LLM call, see Section 3 |
| 6 | Source Credibility Analysis | `ai_engine.credibility` | SourceBadge component | Domain reputation list/heuristics + optional Trusted News API |
| 7 | Fact Verification Report | `reports` (VerificationReport model, FK to Submission) | ReportDetail | Highlights suspicious sentences, cites matching trusted sources |
| 8 | News Search & History | `submissions` (queryset filters) | HistoryList, SearchBar | Per-user history, filter by date/label/confidence |
| 9 | User Feedback Module | `feedback` (Feedback model, FK to Report) | FeedbackForm (thumbs up/down + comment) | Feeds into analytics; optionally into future model retraining |
| 10 | Reports & Analytics Dashboard | `analytics` (aggregation views) | AnalyticsDashboard (charts) | Counts by label, trend over time, top flagged domains; use Recharts/Chart.js |

**Suggested core models:**

```python
# accounts
User (extends AbstractUser) — role: 'user' | 'admin'

# submissions
Submission
  - user (FK)
  - type: 'text' | 'url'
  - raw_content
  - source_url (nullable)
  - created_at

# reports
VerificationReport
  - submission (OneToOne FK)
  - label: 'real' | 'fake' | 'uncertain'
  - confidence_score (float)
  - flagged_statements (JSONField)
  - summary (text)
  - supporting_sources (JSONField)
  - credibility_score (float, nullable)
  - created_at

# feedback
Feedback
  - report (FK)
  - user (FK)
  - is_helpful (bool)
  - comment (text, optional)
  - created_at
```

---

## 3. AI Pipeline (the technically hardest part — plan this first)

Recommended pragmatic pipeline, doable within the timeline:

1. **Preprocessing (NLP):** clean text, sentence-split, strip boilerplate (for URLs, use `newspaper3k` or `trafilatura` for clean article extraction).
2. **ML Classification:** don't train from scratch under time pressure. Options, easiest first:
   - Use a pretrained HuggingFace model fine-tuned for fake-news/misinformation detection (search HF Hub for models trained on datasets like LIAR or FakeNewsNet) and run inference locally.
   - Or train a lightweight baseline (TF-IDF + Logistic Regression/SVM) on a public dataset (LIAR, Kaggle Fake/Real News) as a fallback/complement — good for demonstrating "we built the ML part" in reviews.
3. **LLM API layer:** send the article (or suspicious sentences from step 2) to an LLM with a structured prompt asking for: a verdict, a confidence rationale, a list of specific suspicious claims, and a plain-language summary. Parse as JSON.
4. **Source verification / RAG (optional/stretch):** for key claims, query a trusted-news search API or a small curated vector store of trusted articles, retrieve relevant passages, and pass them to the LLM as context so it can ground its verdict.
5. **Source credibility scoring:** simple heuristic to start — maintain a table/list of known reliable vs. known unreliable domains, score unknown domains as neutral; optional Trusted News API lookup layered on top.
6. **Combine:** final confidence score = weighted blend of ML classifier confidence + LLM verdict confidence + source credibility signal. Document the weighting — reviewers will ask about it.

This hybrid (ML + LLM + heuristic credibility) is realistic to build, testable, and gives you something substantive to explain each week about "AI prediction" without needing a custom-trained deep model.

---

## 4. 13-Day Sprint Plan (if 15.08.2026 is fixed)

MVP-only scope: cut RAG and Trusted News API to stretch goals; ship a working end-to-end pipeline with a solid ML+LLM core.

| Days | Focus | Deliverables |
|------|-------|---------------|
| 1–2 | Setup & Auth | Repo, Django + DRF + JWT, React scaffold, User model, Login/Register working end-to-end |
| 3–4 | Submission + AI core | Submission model/API, text preprocessing, integrate pretrained classifier, basic LLM call returning label+confidence |
| 5–6 | URL verification + Reports | URL scraping → same AI pipeline, VerificationReport model, ReportDetail UI, highlight suspicious statements |
| 7 | Source credibility (heuristic) | Domain reputation list, credibility score merged into report |
| 8 | History & Search | Submission history API + filterable UI |
| 9 | Feedback module | Feedback model + API + UI |
| 10 | Admin dashboard | User management, content moderation views |
| 11 | Analytics dashboard | Aggregation endpoints + charts |
| 12 | Integration testing | Postman collection, bug fixes, edge cases (empty input, non-article URLs) |
| 13 | Polish & deploy/demo prep | README, demo script, deployment (or local run instructions), final QA |

---

## 5. 7-Week Plan (recommended if deadline can move)

| Week | Milestone |
|------|-----------|
| 1 | Requirements finalized, DB schema designed, repo/CI set up, auth (backend+frontend) working |
| 2 | Submission module (text) + URL scraping working; basic ML classifier integrated and returning predictions |
| 3 | LLM API integration for verdict/summary/suspicious-statement extraction; Fact Verification Report model + UI |
| 4 | Source credibility analysis + (stretch) Trusted News API/RAG proof-of-concept |
| 5 | History/Search + Feedback module; Admin dashboard |
| 6 | Analytics dashboard; full API test suite in Postman; end-to-end integration polish |
| 7 | Bug fixing, UI polish, deployment, documentation, demo rehearsal |

---

## 6. Weekly Review Template

Use this every week regardless of which timeline you follow — matches your specified reporting fields.

```
## Weekly Review — Week of [date]

**Completed modules:** 
**Pending modules:** 
**User authentication status:** 
**News submission module progress:** 
**AI fake news detection progress:** 
**Source verification integration status:** 
**Reports dashboard progress:** 
**GitHub code status:** (commits this week, branch state, open PRs)
**UI and API integration progress:** 
**Issues/blockers:** 
**Next week plan:** 
```

---

## 7. Immediate Next Steps

1. Confirm with the student(s) whether 15.08.2026 is truly fixed — if so, formally descope RAG/Trusted News API now, in writing, so it doesn't silently eat time in week 2.
2. Set up the repo with separate `backend/` and `frontend/` folders, and a `docs/` folder for the weekly review notes.
3. Pick the pretrained fake-news classifier and LLM API provider before writing any other code — this is the highest-risk/highest-uncertainty piece and should be validated on day 1–2, not discovered to be a blocker on day 10.
