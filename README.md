# AgentOnWheels TMS

Transport management system (orders, trip scheduling, control tower, fleet, workshop, rates/bids, partners, finance), built as a better replacement for ATS Shipping.
It's one codebase: **Django 6 + DRF (JWT)** serves the API *and* the built **Vue 3 + Vite + Tailwind** app on one server. The database is **Postgres on Neon**.

## Layout
```
config/            Django settings/urls (DATABASE_URL or NEON_DATABASE_URL, sslmode=require)
core/models.py     ~50 domain models + business rules (validation, derived status, numbering)
core/registry.py   one declarative entry per module -> API, filters, columns, wizards, CSV export
core/api.py        generic viewsets + meta endpoints + custom actions (order full/transition, driver passcode, report CSV)
core/services.py   KPI engine (single source of truth) + automatic status expiry
core/management/commands/  seed_demo, expire_statuses
frontend/          Vue 3 SPA (Dashboard, Control tower, generic list/wizard/detail, Order detail)
scripts/build.sh   builds the frontend into Django (templates/index.html + static)
```

## Setup
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env         # put your Neon URL in DATABASE_URL (…?sslmode=require)
python manage.py migrate
python manage.py createsuperuser --username admin
python manage.py seed_demo   # optional demo data (--reset to wipe core data first)
./scripts/build.sh           # npm install + vite build + collectstatic
python manage.py runserver   # or: gunicorn config.wsgi -b 0.0.0.0:8000
```
Open http://localhost:8000 and sign in. If there's no DATABASE_URL/NEON_DATABASE_URL, the app falls back to local SQLite (for development only).

Frontend hot reload: `cd frontend && npm run dev` (it proxies /api to :8000).

## Scheduled jobs
Bids, leases, contracts, quotations and RFQs expire on their own:
```
*/10 * * * * cd /path/AgentOnWheels && .venv/bin/python manage.py expire_statuses
```
(or `python manage.py expire_statuses --loop 600`). The dashboard also runs it on each load.

## API
- `POST /api/auth/login/` returns a JWT pair. `POST /api/auth/refresh/`. `GET /api/auth/me/`
- `GET /api/meta/` and `/api/meta/<module>/`: schema (fields, filters, wizard steps)
- `/api/<module>/`: CRUD with `?search=`, `?ordering=`, `?page=&page_size=`, field filters, `__gte/__lte` dates, plus `/counts/` and `/export/` (CSV)
- `/api/dashboard/?range=7d|30d|90d|mtd&from=&to=&branch=&customer=&job_type=`, `/api/control-tower/`
- `/api/orders/<id>/full/`, `POST /api/orders/<id>/transition/`, `POST /api/drivers/<id>/set_passcode/`, `/api/reports/<id>/download/`

Tests: `python manage.py test core`
