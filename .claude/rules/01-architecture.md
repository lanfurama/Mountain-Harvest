# Architecture Rules

## Layered Architecture (strict top-down flow)
```
Views (Interface) → Services (Business Logic) → Repositories (Data Access) → Models (ORM)
```

### Rules
1. **Views** handle HTTP request/response only. Never call `Model.objects.*` directly from views — go through repositories or services.
2. **Services** contain business logic (filtering, sorting, pagination, fallbacks). Services call repositories, never raw ORM.
3. **Repositories** are the only layer that touches `Model.objects.*`. Return model instances or dicts.
4. **Models** define schema and provide `to_dict()` for serialization. Models never import from other layers.

### File Organization
- One model per file in `api/models/`
- One repository per domain in `api/repositories/`
- One service per domain in `api/services/`
- Views split by concern: `api_views.py` (JSON), `frontend_views.py` (SSR), `admin_views*.py` (admin), `seo_views.py`

### Data Flow Examples
```
GET /api/products → api_views.api_products → ProductService.get_products_with_mock_fallback → ProductRepository.get_all
GET /products/1/  → frontend_views.product_detail → ProductRepository.get_by_id → SSR HTML
POST /admin/...   → admin_views_wrapper → Model CRUD (note: admin bypasses service layer by design)
```

### Adding New Features
- New domain entity? Create: model → repository → service (if logic needed) → view
- New API endpoint? Add to `api/urls.py`, create view in appropriate views file
- New admin CRUD? Add to `admin_views_wrapper.py` (follows existing FastHTML pattern for now)
