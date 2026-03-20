# SkillBridge Career Navigator

> AI-powered skill gap analysis and personalized learning roadmap generator.

---

## Candidate Name
Srishaatvika Selvam 

## Scenario Chosen
**Scenario 2 — Skill-Bridge Career Navigator**

## Estimated Time Spent: 
5 - 6 hours 
---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+ (for frontend)
- Gemini API key (`GEMINI_API_KEY`) for AI-powered analysis
- SerpAPI key (`SERPAPI_KEY`) for live courses/certifications/job suggestions

### Setup

```bash
# 1. Clone the repo
git clone <your-repo-url>
cd skillbridge

# 2. Backend
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY and SERPAPI_KEY if available

pip install -r requirements.txt

# 3. Run the API
uvicorn app.main:app --reload
# API docs available at http://localhost:8000/docs

# 4. Frontend (separate terminal)
cd frontend
npm install
npm run dev
# Open http://localhost:5173
```

### Test Commands

```bash
# Run all tests
pytest tests/ -v
```

---

## Architecture

```
skillbridge/
├── app/
│   ├── main.py        # FastAPI routes
│   ├── analyzer.py    # Gemini API + rule-based fallback + orchestration
│   ├── courses.py     # SerpAPI-powered course & certification enrichment
│   ├── jobs.py        # SerpAPI-powered job suggestions (experience-aware)
│   └── models.py      # Pydantic request/response models
├── data/
│   ├── job_descriptions.json   # Synthetic JD dataset (8 roles)
│   ├── sample_resumes.json     # Synthetic resume samples (4 personas)
│   └── skills_map.json         # Skills taxonomy + learning resources
├── tests/
│   └── test_api.py    # API, edge cases, SerpAPI wiring, helpers
├── frontend/          # React + Vite UI (structured resume form)
├── .env.example       # Safe-to-commit key template
├── .gitignore         # .env excluded
└── requirements.txt
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/roles` | List available job titles |
| GET | `/jobs?role=...` | Get job descriptions (filterable) |
| POST | `/analyze` | Core: resume + role → gap analysis + roadmap + jobs |
| GET | `/sample-resumes` | Synthetic resumes for quick experiments |

### Core Flow

```
User fills structured resume form + selects target role + experience level
        ↓
Frontend composes a resume-like text and POSTs /analyze
        ↓
Backend loads matching JDs from synthetic dataset
        ↓
Try Gemini (gemini-2.5-flash) for structured JSON gap analysis
    ├─ Success → ai_powered: true
    └─ Failure / no key → rule-based keyword fallback (ai_powered: false)
        ↓
Enrich roadmap via SerpAPI: courses + optional certifications per skill
        ↓
Fetch relevant job postings via SerpAPI (experience-aware filtering)
        ↓
Return: missing_skills, transferable_skills, roadmap[], suggested_jobs[], summary
        ↓
Frontend renders skills, learning roadmap, and relevant job postings
```

---

## Key Features

### 1. AI-Powered Gap Analysis (with Safe Fallback)
- **Primary path:** Gemini (`gemini-2.5-flash`) receives the resume text, target role, and relevant job descriptions.
- It returns strict JSON with:
  - `missing_skills`
  - `transferable_skills`
  - `roadmap` (ordered learning items)
  - `summary`
- **Fallback path:** If no `GEMINI_API_KEY` is configured or the call fails, a deterministic rule-based analyzer:
  - Scans resume text for known skills in `skills_map.json`
  - Diffs against required skills in the synthetic JDs
  - Builds an ordered roadmap from the skills map
  - Marks `ai_powered: false` in the response

The API always returns a valid `AnalyzeResponse` — AI failure never crashes the endpoint.

### 2. Live Courses & Certifications via SerpAPI
- For each roadmap skill, `courses.py` optionally calls SerpAPI (`google` engine) to:
  - Find at least one strong primary learning resource (e.g., Coursera/official docs)
  - Add an alternative resource when possible
- It then performs a second SerpAPI search for `"<skill> certification"` and:
  - Extracts up to two reasonable-looking certification titles
  - Falls back to a small static map when SerpAPI is unavailable or returns nothing
- These are added to each `RoadmapItem` as a `certifications` field so the UI can render a
  "Recommended certs" line without depending on live APIs.

### 3. Experience-Aware Job Suggestions
- `jobs.py` uses SerpAPI's `google_jobs` engine to fetch live job postings for the selected role.
- It normalizes results into `SuggestedJob` objects with:
  - `title`, `company`, `location`, `link`, `snippet`
- The query and a small title filter respect the selected `experience_level` (`junior`, `mid`, `senior`):
  - Junior: filters out obviously senior titles (e.g., "Senior", "Lead", "Principal")
  - Mid: neutral
  - Senior: query hints bias towards senior/lead roles
- If `SERPAPI_KEY` is missing or there is a network error, the helper fails gracefully and returns an empty list; the rest of the analysis still works.

### 4. Structured Resume Form (Frontend)
- Instead of pasting raw resume text, the React UI guides the user through a simple form:
  - Name
  - Education
  - One main experience block (role, company, duration, bullet points)
  - Skills (comma-separated)
  - Projects (short free-text)
  - Existing certifications
  - Target role (drop-down from `/roles`)
  - Experience level (junior / mid / senior)
- The frontend then composes these fields into a resume-like string before sending it to `/analyze`,
  so the backend contract remains `resume_text + target_role + experience_level`.

---

## AI & Tooling Disclosure

- **AI assistants used:** GitHub Copilot (coding), Gemini for some prompt experiments.
- **How suggestions were validated:**
  - Read and edited all generated code before committing.
  - Added tests around the core `/analyze` flow, AI fallback, and helper functions.
  - Manually exercised the UI against several roles and resumes.
- **Important customization:**
  - Prompt tuned to enforce **raw JSON only** from Gemini, with a defensive strip of markdown fences
    before `json.loads()` to avoid subtle parsing failures.
  - SerpAPI integrations are treated as **best-effort enrichments**: failures are logged briefly and
    simply result in fewer resources/jobs, never in API errors.

---

## Tradeoffs & Next Steps

### Tradeoffs
- No database or authentication — everything is request-scoped and reads from JSON files.
- Only a single experience block in the form — enough for the prototype, but real resumes can have many.
- Experience-level heuristics for job titles are intentionally simple (keyword-based) to keep logic transparent.

### If I had more time
1. **Testing:**
   - Add unit tests specifically for `courses.enrich_roadmap_with_serpapi` using mocks for SerpAPI.
   - Add more granular tests for `jobs.fetch_relevant_jobs_for_role` (per experience level).
2. **Frontend UX:**
   - Support multiple experience entries and nicer chips for skills/tags.
   - Show loading/error states per enrichment (courses vs jobs) instead of a single spinner.
3. **Data & robustness:**
   - Add simple rate limiting and request size limits on `/analyze`.
   - Expand skills taxonomy and JD coverage, plus synonym support (e.g., "Torch" → "PyTorch").

---

## Tests

Run all tests with:

```bash
pytest tests/ -v
```

Current tests cover:
- **/analyze endpoint**
  - Fallback path when no AI key is configured
  - AI-powered path with mocked Gemini response
  - Rejection of empty resume or target role (400s)
  - Graceful fallback when the AI client raises an exception
  - Roadmap size is capped to a maximum of 6 items
  - `suggested_jobs` field is always present in the response
  - `experience_level` is correctly forwarded into the job suggestion helper
- **Supporting endpoints**
  - `/roles` returns a non-empty list of role strings
  - `/jobs` returns all job descriptions or filters by role
  - `/sample-resumes` returns the synthetic demo data
- **Helper functions**
  - `_extract_skills_from_resume` case-insensitive matching and empty-resume behavior
  - Rule-based fallback when a resume already contains all required skills
  - Junior job-title filtering does not surface obviously senior roles

This gives a reviewer confidence that the core analysis flow, AI fallback, and newer integrations
(SerpAPI wiring, experience_level) behave as intended even when external APIs are unavailable.
