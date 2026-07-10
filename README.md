# Prescription Management System

A web app for doctors to create, manage, and print digital prescriptions — sign up, fill in
a clinic/doctor profile, add patients, write prescriptions, and print/PDF them on a proper
letterhead. It also has subscription plans (Free/Pro/Premium, via Stripe) with a daily
prescription limit per plan, and an admin dashboard to see all doctors, override plans, and
suspend accounts.

This is a two-part app:
- **`backend/`** — a FastAPI (Python) API that owns all the data and business logic.
- **`frontend/`** — a Next.js (React) site doctors and admins actually use in the browser.

## Tech stack

**Backend**
- [FastAPI](https://fastapi.tiangolo.com/) (async) + [Uvicorn](https://www.uvicorn.org/)
- [SQLAlchemy 2.0](https://www.sqlalchemy.org/) (async ORM) + [asyncpg](https://github.com/MagicStack/asyncpg) on **PostgreSQL**
- [Alembic](https://alembic.sqlalchemy.org/) for database migrations
- [Pydantic v2](https://docs.pydantic.dev/) for request/response validation and settings
- [Stripe](https://stripe.com/) (test mode) for subscription billing
- [ReportLab](https://www.reportlab.com/) for PDF prescription generation, Jinja2 for email templates
- [uv](https://docs.astral.sh/uv/) as the package/dependency manager and Python version manager
- [pytest](https://docs.pytest.org/) for tests

**Frontend**
- [Next.js 16](https://nextjs.org/) (App Router) + [React 19](https://react.dev/)
- [TypeScript](https://www.typescriptlang.org/)
- [Tailwind CSS v4](https://tailwindcss.com/) + [shadcn](https://ui.shadcn.com/)-style components built on [Base UI](https://base-ui.com/)
- [react-hook-form](https://react-hook-form.com/) + [zod](https://zod.dev/) for forms/validation
- [Recharts](https://recharts.org/) for the admin dashboard's charts

## Backend folder structure (`backend/`)

```
backend/
  app/
    api/v1/            One file per feature's routes: auth, doctor_profile, patients,
                        prescriptions, billing, admin. router.py wires them all together.
    core/               Cross-cutting stuff: config.py (env-driven Settings), database.py
                        (async engine/session), security.py (password hashing, JWT),
                        cookies.py, plans.py (subscription plan limits).
    models/              SQLAlchemy ORM models — one file per table (User, Patient,
                        Prescription, Subscription, etc).
    schemas/            Pydantic request/response shapes, one file per feature.
    repositories/        All raw database queries live here, one repository per model —
                        services never write SQL/SQLAlchemy queries directly.
    services/           Business logic (one per feature). Routes call services, services
                        call repositories. pdf_service.py renders prescriptions to PDF,
                        email_service.py sends OTP/verification emails.
    templates/emails/    Jinja2 email templates.
    main.py               FastAPI app setup (CORS, routers, /health).
  alembic/               Migration scripts (`alembic/versions/`) + env.py.
  scripts/
    create_admin.py       Creates an admin login directly in the DB (no signup flow for admins).
    db_clean.py            Small dev helper for inspecting/resetting local data.
  tests/                  pytest suite, one file per feature, run against a real Postgres
                        test database (no mocking of the DB).
  pyproject.toml / uv.lock   Dependencies, managed by uv.
```

The layering is always **route → service → repository → model**: routes handle HTTP
concerns and call a service; services hold the actual business rules and call one or more
repositories; repositories are the only place that talks to the database directly.

## Frontend folder structure (`frontend/src/`)

```
frontend/src/
  app/                    Next.js App Router — one folder per route.
    (marketing landing page at app/page.tsx)
    login/, register/, forgot-password/, reset-password/, verify-email/   Auth pages.
    dashboard/            Everything behind doctor login: prescriptions, patients,
                        billing, settings. layout.tsx holds the auth gate + sidebar.
    admin/                Everything behind admin login: the admin dashboard.
                        Separate layout/gate from dashboard/ — different role.
  components/
    ui/                   Generic shadcn-style primitives (button, table, select, card...).
    marketing/             Landing page sections.
    auth/                Login/register/reset-password forms.
    dashboard/             Sidebar, header, and other dashboard chrome.
    admin/                Admin header + the stats/charts section.
    prescriptions/, settings/   Feature-specific components.
  lib/
    api.ts                 Thin fetch wrapper (base URL, CSRF header, error handling).
    auth-context.tsx / subscription-context.tsx   React context providers for "who's
                        logged in" and "what's my plan/usage".
    types.ts               Shared TypeScript types + a few label/lookup maps.
    validation.ts           zod schemas for forms.
  hooks/                    Small reusable hooks (e.g. use-mobile.ts).
```

## Running it

### The fast way: `run.sh`

From the repository root:

```bash
./run.sh
```

This checks you have `uv` and Node installed, sets up `backend/.env` / `frontend/.env.local`
if they don't exist yet (asking for your PostgreSQL connection string the first time),
installs dependencies, runs database migrations, creates a default admin login if one
doesn't already exist, and starts both the backend and frontend. It prints the admin
email/password every time it runs, so you never have to go hunting for them. Press `Ctrl+C`
to stop both servers.

Once it's up:
- Frontend: http://localhost:3000
- Backend API docs: http://localhost:8000/docs

You need **PostgreSQL installed and running** before this will fully work — `run.sh` will
tell you if it can't reach it and let you fix `backend/.env` and try again. Email
(SMTP) and Stripe are optional for just getting the app running — the server still starts
without them, only "send a real email" and "upgrade a plan" won't work until you fill in
`SMTP_*` / `STRIPE_*` in `backend/.env` yourself.

### The step-by-step way

If you'd rather run each step yourself (or `run.sh` fails on something and you want to see
why), here's exactly what it does, spelled out:

**1. Install uv** (manages the backend's Python — this project needs Python 3.12, and uv will
fetch that specific version automatically, so you don't need to separately install Python
yourself):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
If you'd rather manage Python yourself instead of letting uv do it, use
[pyenv](https://github.com/pyenv/pyenv) and `pyenv install 3.12.2`.

**2. Install Node 24** (or at least Node 20.19+/22.13+). The easiest way, especially if your
system already has a different Node version installed, is [nvm](https://github.com/nvm-sh/nvm):
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
nvm install 24 && nvm use 24
```

**3. Have PostgreSQL running**, with a database + user for this app:
```bash
createuser -P prescription_app      # pick a password when prompted
createdb -O prescription_app prescription_mgmt
```

**4. Set up the backend config:**
```bash
cd backend
cp .env.example .env
# edit .env: set DATABASE_URL to match what you created above, and a real SECRET_KEY
# (SMTP_*/STRIPE_* can stay blank for now — only needed for real emails/billing)
```

**5. Install backend deps and migrate the database:**
```bash
uv sync
uv run alembic upgrade head
```

**6. Create an admin login:**
```bash
uv run python scripts/create_admin.py --email admin@example.com --password "Some8Strong!Pass"
```

**7. Start the backend:**
```bash
uv run uvicorn app.main:app --reload --port 8000
```

**8. In a second terminal, set up and start the frontend:**
```bash
cd frontend
cp .env.example .env.local   # default already points at http://localhost:8000/api/v1
npm install
npm run dev
```

Visit http://localhost:3000.

### Running with Docker

`backend/Dockerfile` and `frontend/Dockerfile` build the application images themselves —
neither one bundles a database. Run your own PostgreSQL (locally, in a container, or hosted)
and point `DATABASE_URL` at it.

```bash
# Backend — pass real config via --env-file or -e flags (see backend/.env.example)
docker build -t prescription-backend ./backend
docker run --rm -p 8000:8000 --env-file backend/.env prescription-backend

# Frontend — NEXT_PUBLIC_API_URL is baked in at build time, not runtime
docker build -t prescription-frontend ./frontend \
  --build-arg NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
docker run --rm -p 3000:3000 prescription-frontend
```

The backend image runs pending Alembic migrations automatically on container start, then
launches the API. Create an admin the same way as above, just run it inside the container
(`docker exec -it <container> python scripts/create_admin.py --email ... --password ...`)
or run `scripts/create_admin.py` locally against the same `DATABASE_URL`.

## Running the tests

```bash
cd backend
uv run pytest -v      # needs TEST_DATABASE_URL in .env pointing at a separate test DB
uv run ruff check .    # lint
```

```bash
cd frontend
npx tsc --noEmit   # type-check
npm run lint        # eslint
```
