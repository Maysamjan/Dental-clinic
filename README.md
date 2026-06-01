# 🦷 Dental Clinic Management System

A modern, secure, responsive web-based management system built for dental
clinics in Afghanistan. It supports **offline (LAN)** and **online (cloud)**
deployment, multi-language UI (**Dari / Pashto / English**) with **RTL**
support, **dark/light** themes, and both **Gregorian** and **Solar Hijri**
calendars.

> No mobile app, SMS, WhatsApp, insurance, patient portal, AI, or multi-branch
> functionality in Version 1 (by design).

---

## ✨ Tech Stack

| Layer        | Technology                                                        |
|--------------|-------------------------------------------------------------------|
| Frontend     | Next.js (App Router), React, TypeScript, Tailwind CSS, Zustand, React Query |
| Backend      | Django, Django REST Framework, Django Channels (WebSockets)       |
| Database     | PostgreSQL 16                                                      |
| Realtime     | Redis + Channels                                                  |
| Auth         | JWT (SimpleJWT) + Role-Based Access Control                       |
| Infra        | Docker, Docker Compose, Nginx, Linux                              |

---

## 🚀 Quick Start (Docker)

```bash
cp .env.example .env          # adjust secrets
docker compose up --build
```

Then open:

- App (frontend via Nginx): http://localhost
- API root: http://localhost/api/
- Django admin: http://localhost/django-admin/

Create the first admin user & seed roles/demo data:

```bash
docker compose exec backend python manage.py seed_roles
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py seed_demo   # optional demo data
```

### Local development (without Docker)

**Backend**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DJANGO_SETTINGS_MODULE=config.settings.dev
python manage.py migrate
python manage.py seed_roles
python manage.py runserver
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

---

## 🧱 Architecture

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) and the data model in
[`docs/ERD.md`](docs/ERD.md).

```
Browser ──► Nginx ──┬──► Next.js (SSR/CSR frontend)
                    ├──► Django REST API  (/api)
                    └──► Django Channels  (/ws  WebSockets)
                              │
                  PostgreSQL ─┴─ Redis (channel layer)
```

---

## 👥 Roles

System Administrator · Clinic Manager · Doctor · Receptionist · Accountant ·
Inventory Officer. Permissions are enforced server-side via DRF permission
classes and a role→permission matrix (`apps/accounts`).

## 📦 Modules

Dashboard · Reception/Doctor live workflow · Patients · Appointments · Visits ·
Dental Chart (Odontogram, FDI) · Treatments · Prescriptions · Invoices ·
Payments · Installments · Expenses · Inventory · Documents · Reports ·
Follow-Ups · Administration · Audit & Security · Backup/Restore.

## 🔐 Security

JWT auth, RBAC, Argon2/PBKDF2 password hashing, audit logs, session tracking,
and activity logging for logins, patient/invoice/payment record changes.

## 💾 Backup & Recovery

```bash
docker compose exec backend python manage.py backup_db      # manual backup
docker compose exec backend python manage.py restore_db <file>
```
Scheduled backups can be wired via cron or a Celery beat task.

---

## 📁 Repository Layout

```
backend/    Django + DRF + Channels project (apps per domain)
frontend/   Next.js + TypeScript + Tailwind app
nginx/      Reverse proxy config
docs/       Architecture, ERD, API design
docker-compose.yml
```
