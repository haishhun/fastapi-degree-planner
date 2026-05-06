# CS Degree Planner — Full-Stack Project Roadmap
**Client:** Dzmitry / Hunter College CS Degree Planner
**Prepared by:** Business Analysis
**Date:** May 2026
**Stack:** FastAPI (Python) · SQLite/PostgreSQL · Vanilla JS or React (same design)

---

## Executive Summary

The client currently has a **static, hand-coded HTML file** that tracks their personal CS degree plan at Hunter College. Every time something changes (a new grade, a new course enrolled, a prereq cleared), they must open the file in a text editor and manually update numbers. There is no persistence, no login, no way to share progress with an advisor, and no automatic recalculation.

The goal is to convert this into a **real web application** with a FastAPI backend that stores all data in a database. The frontend keeps the exact same dark-themed visual design. The student (or an advisor) can log in, edit courses, record grades, and have all stats — credits applied, degree progress %, remaining requirements — recalculated automatically.

---

## Part 1 — Backend (FastAPI)

### 1.1 What the Backend Needs to Do (in plain terms)

1. Store all courses the student has taken, is taking, or plans to take.
2. Store the full Hunter CS degree requirements (the rules — not per-student, but fixed).
3. When a course is added, updated, or deleted, automatically recompute all stats (total credits, CS credits, % complete, GPA, etc.).
4. Expose all of that data via a clean REST API so the frontend can just fetch it.
5. Handle a basic login so the data is private.

---

### 1.2 Data Models

#### `User`
| Field | Type | Notes |
|---|---|---|
| `id` | int (PK) | auto |
| `name` | string | e.g. "Haishun, Dzmitry" |
| `email` | string | unique |
| `hashed_password` | string | bcrypt |
| `college` | string | "Hunter College" |
| `major` | string | "Computer Science" |
| `degree_type` | string | "BA" |
| `created_at` | datetime | |

#### `Course` (the master catalog — fixed, not per student)
| Field | Type | Notes |
|---|---|---|
| `id` | int (PK) | |
| `code` | string | e.g. "CSCI 12700" |
| `name` | string | e.g. "Intro to Computer Science" |
| `credits` | int | |
| `category` | enum | `CORE`, `MATH`, `ELECTIVE`, `GEN_ED` |
| `is_cs_elective_eligible` | bool | courses 26700+ |
| `prereq_description` | string | human-readable, e.g. "MATH 15000" |
| `prereq_course_ids` | list[int] | FK to other courses (for validation) |
| `min_grade_required` | string | "C" or "D+" depending on course |

#### `StudentCourse` (the enrollment record — one per student per course)
| Field | Type | Notes |
|---|---|---|
| `id` | int (PK) | |
| `user_id` | int (FK → User) | |
| `course_id` | int (FK → Course) | |
| `semester` | string | "Spring 2026" |
| `status` | enum | `COMPLETE`, `IN_PROGRESS`, `ENROLLED`, `PLANNED` |
| `grade` | string | nullable — "A", "B+", "C", etc. |
| `grade_points` | float | computed from grade |
| `credits_applied` | int | copied from Course at enrollment time |

#### `DegreeRequirement` (fixed rules for CS BA at Hunter)
| Field | Type | Notes |
|---|---|---|
| `id` | int (PK) | |
| `name` | string | e.g. "CS Core", "Math Requirement", "CS Electives" |
| `credits_required` | int | |
| `category_filter` | enum | which StudentCourse categories count |
| `notes` | string | e.g. "FS courses cannot overlap with Major" |

---

### 1.3 API Endpoints

All routes under `/api/v1/`. Auth uses **JWT Bearer tokens**.

#### Auth
| Method | Path | What it does |
|---|---|---|
| `POST` | `/auth/register` | Create account |
| `POST` | `/auth/login` | Returns JWT token |
| `GET` | `/auth/me` | Returns current user info |

#### Courses (student's personal plan)
| Method | Path | What it does |
|---|---|---|
| `GET` | `/courses/` | Get all student's courses, grouped by semester |
| `POST` | `/courses/` | Add a course to the plan |
| `PATCH` | `/courses/{id}` | Update grade, status, semester |
| `DELETE` | `/courses/{id}` | Remove a course from the plan |

#### Stats (auto-computed, never manually set)
| Method | Path | What it does |
|---|---|---|
| `GET` | `/stats/` | Returns the full dashboard stats object (see below) |

The `/stats/` endpoint returns a single JSON object the frontend uses to render every card, progress bar, and checklist. It should look like:

```json
{
  "credits_applied": 64,
  "credits_required": 120,
  "degree_progress_pct": 41,
  "credits_remaining": 56,
  "cs_credits_done": 11,
  "cs_credits_required": 45,
  "cs_credits_remaining": 34,
  "gpa_cumulative": 3.5,
  "gpa_cs_only": 3.6,
  "est_graduation": "Spring 2029",
  "liberal_arts_credits": 46.5,
  "requirements": [
    {
      "name": "CS Core Courses",
      "credits_done": 7,
      "credits_required": 21,
      "status": "IN_PROGRESS",
      "items": [...]
    },
    ...
  ]
}
```

#### Catalog (read-only reference data)
| Method | Path | What it does |
|---|---|---|
| `GET` | `/catalog/courses` | All courses in the Hunter CS catalog |
| `GET` | `/catalog/courses/{code}` | Single course with prereqs |
| `GET` | `/catalog/requirements` | All degree requirements |

#### Prereq Validation
| Method | Path | What it does |
|---|---|---|
| `POST` | `/prereqs/check` | Given a course code, returns whether prereqs are met based on current plan, and what's missing |

---

### 1.4 Business Logic (computed server-side, not stored)

These are calculations the backend performs every time `/stats/` is called. **Never hardcode these values** — they must be derived from the database.

- **Credits Applied**: sum of `credits_applied` for all `StudentCourse` records where `status = COMPLETE or IN_PROGRESS`.
- **Degree Progress %**: `credits_applied / 120 * 100`, rounded.
- **GPA**: standard grade-point calculation. Map letter grades to points (A=4.0, A-=3.7, B+=3.3, etc.). Weighted average by credits.
- **CS Credits**: filter `StudentCourse` by `course.category IN (CORE, MATH, ELECTIVE)` and sum credits.
- **Requirement fulfillment**: for each `DegreeRequirement`, check how many credits from the relevant categories have been completed.
- **Prereq readiness**: a course is "ready" if all its `prereq_course_ids` have `status = COMPLETE` (or `IN_PROGRESS` for concurrent prereqs, as noted in the current HTML).

---

### 1.5 Project Structure

```
backend/
├── main.py                  # FastAPI app, CORS, startup
├── database.py              # SQLAlchemy engine + session
├── models/
│   ├── user.py
│   ├── course.py
│   ├── student_course.py
│   └── degree_requirement.py
├── schemas/
│   ├── user.py              # Pydantic request/response models
│   ├── course.py
│   └── stats.py
├── routers/
│   ├── auth.py
│   ├── courses.py
│   ├── stats.py
│   └── catalog.py
├── services/
│   ├── stats_service.py     # All the computation logic lives here
│   └── prereq_service.py
├── seed_data/
│   └── hunter_cs_catalog.py # Script to pre-populate catalog and requirements
├── requirements.txt
└── .env                     # DATABASE_URL, SECRET_KEY
```

---

### 1.6 Tech Stack (Backend)

| Concern | Choice | Why |
|---|---|---|
| Framework | FastAPI | Fast, modern, auto-generates docs at `/docs` |
| ORM | SQLAlchemy 2.0 | Standard, works with SQLite for dev and Postgres for prod |
| Database (dev) | SQLite | Zero setup, single file |
| Database (prod) | PostgreSQL | Reliable, free tier on Railway/Supabase |
| Auth | python-jose + passlib | JWT + bcrypt, well-supported |
| Validation | Pydantic v2 | Built into FastAPI |
| Migrations | Alembic | For schema changes without dropping tables |

**`requirements.txt`**
```
fastapi
uvicorn[standard]
sqlalchemy
alembic
python-jose[cryptography]
passlib[bcrypt]
pydantic[email]
python-dotenv
```

---

### 1.7 How to Run (dev)

```bash
cd backend
pip install -r requirements.txt
python seed_data/hunter_cs_catalog.py   # populate catalog once
uvicorn main:app --reload
# API docs at http://localhost:8000/docs
```

---

## Part 2 — Frontend

### 2.1 What Changes vs the Current HTML File

The current HTML file has **all data hardcoded in the HTML itself**. The new frontend is the same visual design but:

- All data is **fetched from the API** on page load (`GET /api/v1/stats/`, `GET /api/v1/courses/`)
- The student can **click a course and edit it** (change status, add a grade)
- Stat cards, progress bars, and requirement checklists **update automatically** after any change
- There is a **login screen** before the dashboard

Everything else — the dark background, the grid texture, the Syne font headings, the tab layout, the colored status pills, the collapsible semesters — stays exactly the same.

---

### 2.2 Pages / Views

#### 1. Login Page (`/login`)
Simple centered card on the dark background. Email + password fields. On success, stores the JWT in `localStorage` and redirects to the dashboard.

#### 2. Dashboard (`/`)
This is the current HTML file, refactored. Same 4-tab layout:
- **Timeline** — semester blocks, fetched from API, collapsible
- **Requirements** — checklist, driven by `/stats/requirements`
- **Prereq Map** — course cards with readiness pills, derived from catalog + student plan
- **Electives** — static reference data (can stay hardcoded or come from catalog API)

The 5 stat cards at the top are rendered from the `/stats/` response.

---

### 2.3 Frontend Stack Options

**Option A — Keep it plain HTML/JS (simplest)**
Keep the single HTML file. Replace hardcoded data with `fetch()` calls. Add a login page as a separate `login.html`. This is the easiest path if you want to stay close to what you have.

**Option B — React (recommended for long term)**
Convert to a React app (Vite). Components map 1-to-1 to the current HTML sections. Same CSS variables and styles. Better for handling state (editing a course, refreshing stats, etc.).

The roadmap below uses React since it's cleaner for a real app, but the API is identical either way.

---

### 2.4 React Component Tree

```
App
├── AuthProvider (manages JWT, login state)
├── LoginPage
└── DashboardLayout
    ├── Header (student name, audit date)
    ├── StatsGrid
    │   └── StatCard × 5 (credits applied, progress %, remaining, CS credits, graduation)
    ├── TabBar (Timeline / Requirements / Prereq Map / Electives)
    └── TabContent
        ├── TimelineTab
        │   ├── SemesterBlock × N (collapsible)
        │   │   └── CourseRow × N
        │   │       └── CourseEditModal (on click)
        │   └── Sidebar
        │       ├── RequirementsChecklist (mini version)
        │       └── CreditBreakdownBars
        ├── RequirementsTab
        │   └── RequirementCard × N
        ├── PrereqMapTab
        │   └── PrereqCard × N (with readiness pill)
        └── ElectivesTab
            └── ElectiveCard × N
```

---

### 2.5 API Integration (Frontend)

```javascript
// Example: load dashboard on mount
useEffect(() => {
  const token = localStorage.getItem('token');
  fetch('/api/v1/stats/', {
    headers: { Authorization: `Bearer ${token}` }
  })
    .then(r => r.json())
    .then(data => setStats(data));

  fetch('/api/v1/courses/', {
    headers: { Authorization: `Bearer ${token}` }
  })
    .then(r => r.json())
    .then(data => setCourses(data));
}, []);

// Example: update a course grade
async function updateCourse(id, patch) {
  const res = await fetch(`/api/v1/courses/${id}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`
    },
    body: JSON.stringify(patch)
  });
  // After update, re-fetch stats so all cards recalculate
  if (res.ok) refetchStats();
}
```

---

### 2.6 Course Edit Interaction

When a student clicks on a course row in the Timeline tab, a small modal/panel slides in (same dark surface style) with:
- Status dropdown: `Complete / In Progress / Enrolled / Planned`
- Grade input (only shown if status = Complete): A, A-, B+, B, B-, C+, C, D+, D, F
- Semester field (text or dropdown)
- Save / Cancel buttons

On Save → `PATCH /api/v1/courses/{id}` → re-fetch stats → all cards update.

---

### 2.7 Frontend Project Structure (React / Vite)

```
frontend/
├── index.html
├── vite.config.js
├── src/
│   ├── main.jsx
│   ├── App.jsx
│   ├── api.js              # all fetch wrappers in one file
│   ├── styles/
│   │   └── globals.css     # the CSS variables from the original file
│   ├── pages/
│   │   ├── LoginPage.jsx
│   │   └── DashboardPage.jsx
│   ├── components/
│   │   ├── Header.jsx
│   │   ├── StatCard.jsx
│   │   ├── TabBar.jsx
│   │   ├── SemesterBlock.jsx
│   │   ├── CourseRow.jsx
│   │   ├── CourseEditModal.jsx
│   │   ├── RequirementCard.jsx
│   │   ├── PrereqCard.jsx
│   │   └── ElectiveCard.jsx
│   └── hooks/
│       ├── useStats.js      # fetches /stats/ and refetch helper
│       └── useCourses.js    # fetches /courses/ grouped by semester
```

---

### 2.8 How to Run (frontend dev)

```bash
cd frontend
npm create vite@latest . -- --template react
npm install
npm run dev
# runs at http://localhost:5173
# proxies /api/* to http://localhost:8000 (configure in vite.config.js)
```

---

## Part 3 — Deployment (when ready)

| What | Where | Cost |
|---|---|---|
| FastAPI backend | Railway.app or Render.com | Free tier |
| PostgreSQL | Railway or Supabase | Free tier |
| React frontend | Vercel or Netlify | Free tier |
| Custom domain | Optional | ~$10/yr |

For local dev both frontend and backend can run simultaneously — the Vite dev server proxies API calls to FastAPI so there's no CORS issue in development.

---

## Part 4 — Build Order (Recommended)

1. **Backend first**: set up models, seed the Hunter CS catalog, implement `/stats/` and `/courses/` endpoints. Verify everything in FastAPI's auto-generated docs at `/docs`.
2. **Frontend skeleton**: get the dashboard rendering real data from the API using plain `fetch()`, keeping all the existing CSS intact.
3. **Auth**: add login page + JWT to both sides.
4. **Edit flow**: wire up the course edit modal so grades and statuses are editable.
5. **Polish + deploy**: move SQLite to Postgres, deploy to Render + Vercel.

---

*This roadmap covers everything needed to take the existing static HTML and turn it into a fully functional, data-driven web application without changing the visual design the client already has.*
