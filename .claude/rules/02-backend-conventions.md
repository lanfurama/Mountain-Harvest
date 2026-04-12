# Backend Conventions (Python/Django)

## Naming
- **Models**: CamelCase (`Product`, `SiteConfig`)
- **DB tables**: lowercase plural, set in `Meta.db_table` (`products`, `site_config`)
- **Files**: snake_case (`product_repository.py`, `site_config.py`)
- **Fields**: snake_case in Python (`created_at`), camelCase in API JSON via `to_dict()`

## Models
- All models in `api/models/`, one per file
- Export in `api/models/__init__.py`
- Every model has `to_dict()` method for JSON serialization (converts snake_case → camelCase)
- Use `created_at`/`updated_at` auto-timestamps where applicable
- Register in `INSTALLED_APPS` via `api.apps.ApiConfig`

## Repositories (static methods pattern)
```python
class ProductRepository:
    @staticmethod
    def get_all(**filters):
        queryset = Product.objects.all()
        # Apply filters using Q objects
        return queryset

    @staticmethod
    def get_by_id(id):
        try:
            return Product.objects.get(id=id)
        except Product.DoesNotExist:
            return None
```

## Services (static methods pattern)
```python
class ProductService:
    @staticmethod
    def get_products_with_mock_fallback(page=1, limit=8, **filters):
        try:
            items = ProductRepository.get_all(**filters)
            # Business logic: filtering, sorting, pagination
            return {"items": [...], "total": n, "page": page}
        except Exception as e:
            logger.warning(f"DB error, using mock: {e}")
            return ProductService._mock_products()
```

## Error Handling
- Always log exceptions before fallback: `logger.warning(f"Context: {e}", exc_info=True)`
- Never use bare `except Exception:` without logging
- Views return appropriate HTTP responses (404, 500, redirect)
- API views return JSON error responses

## Settings
- All secrets via `os.getenv()` — never hardcode
- Database URL via `dj-database-url`
- `DEBUG` from env, defaults to `False`
- Static files served from `public/` directory
