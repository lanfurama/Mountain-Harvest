# Mountain Harvest - Project Guide

## Overview
Mountain Harvest is an e-commerce CMS for agricultural products, built with **Django 4.2** backend + **Vanilla JS** frontend. PostgreSQL database, SSR for SEO, admin panel with Basic Auth.

## Quick Start
```bash
pip install -r requirements.txt
# Configure .env (copy from .env.example)
python manage.py migrate
python run.py  # Dev server on localhost:3005
```

## Architecture
**Layered architecture** (Views → Services → Repositories → Models):
- `api/views/` — HTTP handlers (API JSON + SSR HTML + Admin)
- `api/services/` — Business logic (ProductService, NewsService)
- `api/repositories/` — Data access layer (ORM queries)
- `api/models/` — Django models with `to_dict()` serialization

## Tech Stack
- **Backend**: Django 4.2, PostgreSQL, psycopg2-binary, python-dotenv
- **Frontend**: Vanilla JS (modular), Tailwind CSS (CDN), Font Awesome
- **Fonts**: Playfair Display (serif headlines), Nunito Sans (body), Inter (UI)
- **Auth**: Basic HTTP Auth middleware for `/admin/` routes
- **Design**: Claude/Anthropic-inspired warm parchment aesthetic (see DESIGN.md)

## Key Directories
```
mountain_harvest/    # Django settings, urls, wsgi/asgi
api/                 # Main Django app (models, views, services, repos)
public/              # Static frontend (HTML, CSS, JS)
sql/                 # Database scripts
```

## Rules
See `.claude/rules/` for detailed conventions:
- `01-architecture.md` — Layer rules and data flow
- `02-backend-conventions.md` — Python/Django patterns
- `03-frontend-conventions.md` — JavaScript/CSS patterns
- `04-design-system.md` — Visual design guidelines
- `05-api-patterns.md` — API response formats and routing
- `06-admin.md` — Admin panel specifics
- `07-known-debt.md` — Known tech debt and migration notes

## Important Notes
- **No tests exist yet** — be careful with refactors
- **FastHTML dependency** still present in admin views (migration artifact)
- **Vietnamese** is the primary UI language (i18n in `public/js/i18n.js`)
- `.env` contains DB credentials and admin auth — never commit it
- All secrets loaded from environment variables
