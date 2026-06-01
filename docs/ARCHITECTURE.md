# System Architecture

## 1. Overview

The Dental Clinic Management System is a multi-tier web application:

- **Presentation tier** — Next.js (React/TypeScript) single-page-ish app with
  server-side rendering for fast first load. State via Zustand, server cache via
  React Query.
- **Application tier** — Django + Django REST Framework exposes a versioned REST
  API. Django Channels (ASGI) provides WebSocket endpoints for the real-time
  reception/doctor workflow and live dashboard.
- **Data tier** — PostgreSQL for relational data; Redis as the Channels layer
  and cache backend; local/volume filesystem (or S3-compatible storage online)
  for documents and images.

All HTTP/WS traffic is fronted by **Nginx**, which terminates connections,
serves static/media assets, and reverse-proxies `/api` and `/ws` to Django and
everything else to Next.js.

```
                 ┌─────────────────────────────────────────┐
   Browser  ───► │                  Nginx                  │
 (desktop/       └───────┬───────────────┬─────────────────┘
  laptop/                │ / (SSR)       │ /api  /ws  /static /media
  tablet)        ┌───────▼──────┐  ┌─────▼───────────────────────┐
                 │  Next.js     │  │  Django (ASGI / Daphne)     │
                 │  frontend    │  │  DRF  +  Channels           │
                 └──────────────┘  └───────┬───────────┬─────────┘
                                           │           │
                                   ┌───────▼───┐  ┌────▼─────┐
                                   │PostgreSQL │  │  Redis   │
                                   └───────────┘  └──────────┘
```

## 2. Backend application structure

Domain-driven apps under `backend/apps/`:

| App            | Responsibility                                                |
|----------------|---------------------------------------------------------------|
| `core`         | Base abstract models, mixins, pagination, common permissions, WS consumers |
| `accounts`     | Custom User, Role, RBAC permission matrix, JWT, sessions       |
| `audit`        | Activity/audit logging (signals + middleware)                  |
| `patients`     | Patient records, medical history, archiving                    |
| `appointments` | Scheduling, calendar, statuses                                 |
| `visits`       | Clinical visits, queue/workflow state machine                  |
| `dental_charts`| Odontogram, teeth (FDI), per-tooth conditions & history        |
| `treatments`   | Treatment plans, stages, progress tracking                     |
| `prescriptions`| Prescriptions + PDF export                                     |
| `billing`      | Invoices, payments, installments                               |
| `expenses`     | Clinic expenses by category                                    |
| `inventory`    | Items, stock transactions, low-stock alerts                    |
| `documents`    | Patient images/X-rays/OPG/PDF/lab files                        |
| `followups`    | Internal reminders & follow-up dashboard data                  |
| `reports`      | Aggregations + PDF/Excel export                                |
| `dashboard`    | Aggregated KPIs + real-time broadcast                          |

### Layering inside each app
`models.py` → `serializers.py` → `permissions.py` → `views.py` (DRF
ViewSets) → `urls.py`. Cross-cutting business rules live in `services.py`
where present. Signals broadcast workflow/dashboard changes to Channels groups.

## 3. Real-time workflow

- Receptionist marks a patient **Arrived** → a `Visit` is created/updated with
  status `WAITING` and enqueued.
- A `post_save` signal publishes to the `clinic_workflow` channel group.
- Doctor and reception dashboards subscribe via `/ws/workflow/` and receive
  live queue updates: name, queue number, arrival time, medical-history summary.
- Status flow: `WAITING → IN_CONSULTATION → TREATMENT_IN_PROGRESS → COMPLETED`.
- The dashboard subscribes to `/ws/dashboard/` for live KPI refresh.

## 4. Authentication & RBAC

- JWT via `djangorestframework-simplejwt` (access + refresh, rotation +
  blacklist).
- Each `User` has exactly one `Role`; each `Role` maps to a set of permission
  codes. DRF permission classes (`HasModulePermission`) check the action's
  required permission against the user's role matrix.
- Passwords hashed with Argon2 (fallback PBKDF2). Sessions and logins recorded
  in `accounts.UserSession` and `audit.ActivityLog`.

## 5. Localization & calendars

- `django-modeltranslation`-free approach: UI strings localized in the frontend
  (`next-intl`-style dictionaries for en/fa/ps). API returns ISO dates; the
  frontend converts to Gregorian or Solar Hijri for display.
- RTL handled at the layout level based on the active locale.

## 6. Deployment modes

- **Offline / LAN** — `docker compose up` on a local Linux server; clients reach
  it over the LAN. Backups to a mounted volume.
- **Online / Cloud** — same compose with `config.settings.prod`, TLS terminated
  at Nginx (or a load balancer), media on object storage.

## 7. Security highlights

JWT rotation + blacklist · RBAC enforced server-side · Argon2 hashing · audit &
activity logs · session tracking · CORS allow-list · request size limits at
Nginx · environment-based secrets.
