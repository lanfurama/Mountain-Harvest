# Admin Panel

## Access
- URL: `/admin/`
- Auth: HTTP Basic Authentication (middleware in `api/middleware/auth.py`)
- Credentials: `ADMIN_USER` and `ADMIN_PASSWORD` from `.env`

## Architecture (migration note)
- Admin views use **FastHTML** for HTML generation — this is a migration artifact
- `api/views/admin_views.py` — FastHTML component builders (uses `from fasthtml.common import *`)
- `api/views/admin_views_wrapper.py` — Django view wrappers that call FastHTML builders
- **Do NOT add new FastHTML dependencies** — plan is to migrate to Django templates

## Features
- Dashboard with entity counts
- CRUD for: Products, News, Categories, Pages, Hero sections, Site Config, Category Brochures
- Image URL management (no file upload — URLs to external images)
- SEO fields: meta_title, meta_description, h1/h2/h3 custom tags

## When Editing Admin
- Follow existing patterns in `admin_views_wrapper.py`
- Admin bypasses service layer — direct model/repository access is acceptable here
- Always validate input server-side
- Use existing `MockRequest` adapter for FastHTML compatibility
