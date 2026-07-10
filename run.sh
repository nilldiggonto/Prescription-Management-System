#!/usr/bin/env bash
#
# run.sh — one-command way to get the Prescription Management System running locally.
#
# What this does, in order:
#   1. Checks you have the tools this project needs (uv, Node) and tells you how to get
#      them if not.
#   2. Makes sure backend/.env and frontend/.env.local exist, and walks you through
#      setting DATABASE_URL if it hasn't been set yet.
#   3. Installs backend + frontend dependencies.
#   4. Applies database migrations.
#   5. Creates a default admin login (skipped if one already exists) and prints its
#      credentials — every run, not just the first, so you never have to go dig for them.
#   6. Starts the backend (FastAPI/uvicorn) and frontend (Next.js) dev servers together.
#      Ctrl+C stops both.
#
# If you'd rather do this by hand, or something below fails, each step is a plain command
# you can copy out and run yourself — see README.md for the same steps written out.
#
# Usage:
#   ./run.sh
#   ADMIN_EMAIL=me@example.com ADMIN_PASSWORD='Something8Chars!' ./run.sh   # custom admin login

set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

# ---------------------------------------------------------------------------------------
# 0. Small helpers
# ---------------------------------------------------------------------------------------

info()  { printf '\n\033[1;34m==>\033[0m %s\n' "$1"; }
warn()  { printf '\033[1;33mwarning:\033[0m %s\n' "$1" >&2; }
die()   { printf '\033[1;31merror:\033[0m %s\n' "$1" >&2; exit 1; }

gen_secret() {
    # No dependency on a system python3 — uv only guarantees a *project* python, which
    # isn't necessarily on PATH. openssl is virtually always present; /dev/urandom is the
    # fallback of last resort.
    if command -v openssl >/dev/null 2>&1; then
        openssl rand -hex 32
    else
        head -c 32 /dev/urandom | od -An -tx1 | tr -d ' \n'
    fi
}

# ---------------------------------------------------------------------------------------
# 1. Check required tools
# ---------------------------------------------------------------------------------------

info "Checking required tools"

if ! command -v uv >/dev/null 2>&1; then
    die "uv is not installed. Install it with:
    curl -LsSf https://astral.sh/uv/install.sh | sh
  then open a new shell and re-run ./run.sh.
  (uv manages the backend's Python 3.12 automatically — you do NOT need to separately
  install Python or pyenv unless you specifically want a system-wide 3.12. If you do:
  https://github.com/pyenv/pyenv#installation, then \`pyenv install 3.12.2\`.)"
fi
echo "  uv: $(uv --version)"

if ! command -v node >/dev/null 2>&1; then
    die "Node.js is not installed. This project needs Node 24 (or >=20.19 / >=22.13).
  Easiest way to get it and switch freely between versions later is nvm:
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
  then open a new shell and run:
    nvm install 24 && nvm use 24
  and re-run ./run.sh."
fi

NODE_MAJOR="$(node -v | sed -E 's/^v([0-9]+).*/\1/')"
if [ "$NODE_MAJOR" -lt 20 ]; then
    die "Node $(node -v) found, but this project needs Node 24 (or >=20.19 / >=22.13).
  If you use nvm:  nvm install 24 && nvm use 24   — then re-run ./run.sh."
fi
if [ "$NODE_MAJOR" -lt 24 ]; then
    warn "Node $(node -v) found. Node 24 is recommended (this is what the project was built/tested against); continuing anyway."
fi
echo "  node: $(node -v)"
echo "  npm:  $(npm -v)"

# ---------------------------------------------------------------------------------------
# 2. Backend env file — backend/.env
# ---------------------------------------------------------------------------------------

info "Checking backend configuration (backend/.env)"

if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    echo "  Created backend/.env from backend/.env.example."
fi

CURRENT_DB_URL="$(grep -E '^DATABASE_URL=' backend/.env | head -n1 | cut -d= -f2-)"

if [ -z "$CURRENT_DB_URL" ] || [[ "$CURRENT_DB_URL" == *"changeme"* ]]; then
    echo
    echo "  This app needs a PostgreSQL database to connect to."
    echo "  Make sure PostgreSQL is installed and running, and that a database + user for"
    echo "  this app already exist, e.g.:"
    echo "    createuser -P prescription_app"
    echo "    createdb -O prescription_app prescription_mgmt"
    echo

    if [ -t 0 ]; then
        read -rp "  Enter your DATABASE_URL [postgresql+asyncpg://prescription_app:changeme@localhost:5432/prescription_mgmt]: " input_db_url
        input_db_url="${input_db_url:-postgresql+asyncpg://prescription_app:changeme@localhost:5432/prescription_mgmt}"
        sed -i.bak "s|^DATABASE_URL=.*|DATABASE_URL=${input_db_url}|" backend/.env && rm -f backend/.env.bak
        echo "  Saved DATABASE_URL to backend/.env."
    else
        warn "Not running interactively — leaving the placeholder DATABASE_URL in backend/.env."
        warn "Edit backend/.env yourself and re-run ./run.sh, or the next step will fail."
    fi
fi

CURRENT_SECRET="$(grep -E '^SECRET_KEY=' backend/.env | head -n1 | cut -d= -f2-)"
if [ -z "$CURRENT_SECRET" ] || [[ "$CURRENT_SECRET" == "change-me-to-a-random-secret" ]]; then
    NEW_SECRET="$(gen_secret)"
    sed -i.bak "s|^SECRET_KEY=.*|SECRET_KEY=${NEW_SECRET}|" backend/.env && rm -f backend/.env.bak
    echo "  Generated a random SECRET_KEY."
fi

# SMTP (outgoing email — signup verification/password reset OTPs) and Stripe (billing) are
# both optional for just getting the app running: the server will still start with these
# left blank, only the features that use them (sending an email, upgrading a plan) will
# fail until you fill them in. Not prompting for them here on purpose — see README.md.
if grep -qE '^SMTP_USERNAME=your-email@gmail.com$' backend/.env 2>/dev/null || ! grep -qE '^STRIPE_SECRET_KEY=' backend/.env 2>/dev/null; then
    warn "SMTP and/or Stripe settings in backend/.env still look unconfigured."
    warn "That's fine to get the app running — but signup emails and plan upgrades won't"
    warn "work until you fill in the SMTP_* and STRIPE_* values in backend/.env yourself."
fi

# ---------------------------------------------------------------------------------------
# 3. Frontend env file — frontend/.env.local
# ---------------------------------------------------------------------------------------

info "Checking frontend configuration (frontend/.env.local)"

if [ ! -f frontend/.env.local ]; then
    cp frontend/.env.example frontend/.env.local
    echo "  Created frontend/.env.local from frontend/.env.example (points at http://localhost:8000/api/v1)."
fi

# ---------------------------------------------------------------------------------------
# 4. Install dependencies
# ---------------------------------------------------------------------------------------

info "Installing backend dependencies (uv sync)"
(cd backend && uv sync)

info "Installing frontend dependencies (npm install)"
(cd frontend && npm install)

# ---------------------------------------------------------------------------------------
# 5. Database migrations
# ---------------------------------------------------------------------------------------

info "Applying database migrations (alembic upgrade head)"
if ! (cd backend && uv run alembic upgrade head); then
    die "Migrations failed — this almost always means PostgreSQL isn't running, or
  DATABASE_URL in backend/.env doesn't point at a reachable database/user that exists.
  Fix backend/.env and re-run ./run.sh."
fi

# ---------------------------------------------------------------------------------------
# 6. Default admin user (idempotent — safe to run every time)
# ---------------------------------------------------------------------------------------

ADMIN_EMAIL="${ADMIN_EMAIL:-admin@example.com}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-ChangeMe123!}"

info "Ensuring a default admin account exists"
ADMIN_OUTPUT="$(cd backend && uv run python scripts/create_admin.py --email "$ADMIN_EMAIL" --password "$ADMIN_PASSWORD" --yes 2>&1)" && ADMIN_CREATED=1 || ADMIN_CREATED=0

if [ "$ADMIN_CREATED" = "1" ]; then
    echo "  Created admin account."
elif echo "$ADMIN_OUTPUT" | grep -qi "already exists"; then
    echo "  Admin account already exists — leaving it as-is."
else
    warn "Couldn't confirm the admin account was created. Output was:"
    echo "$ADMIN_OUTPUT" >&2
fi

# ---------------------------------------------------------------------------------------
# 7. Run both servers
# ---------------------------------------------------------------------------------------

cleanup() {
    trap - EXIT INT TERM
    echo
    info "Stopping servers"
    # Signals the whole process group (this script + both dev servers + any of their own
    # child processes, e.g. Next.js's compiler worker) — killing just the two PIDs below
    # isn't enough, `next dev` in particular spawns a child that survives that.
    kill 0 2>/dev/null || true
}
trap cleanup EXIT INT TERM

info "Starting backend on http://localhost:8000 and frontend on http://localhost:3000"
echo "  Press Ctrl+C to stop both."

(cd backend && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000) &
(cd frontend && npm run dev) &

echo
echo "================================================================================"
echo " Admin login"
echo "   Email:    $ADMIN_EMAIL"
echo "   Password: $ADMIN_PASSWORD"
echo "   (This is only the actual password if this is the first time it was created, or"
echo "    you're using the same ADMIN_EMAIL/ADMIN_PASSWORD you set before. Change it via"
echo "    the app once you're in, or delete the row and re-run with different env vars.)"
echo "================================================================================"
echo

wait
