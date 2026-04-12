# Known Technical Debt

## FastHTML → Django Migration (incomplete)
- Admin views still depend on `python-fasthtml` package for HTML rendering
- Target: migrate to Django templates (`templates/admin/`)
- Files affected: `api/views/admin_views.py`, `api/views/admin_views_wrapper.py`

## Frontend Refactoring (documented in `public/js/REFACTORING.md`)
- `products.js` and `news.js` use raw `fetch` instead of `ApiClient`
- `cart.js` has duplicate `formatCurrency` (should use `Utils.formatCurrency`)
- `cart.js` uses raw `localStorage` (should use `Utils.getStorage`)
- Local constants duplicate `Config.*` values (`PRODUCTS_PER_PAGE`, `NEWS_PER_PAGE`)
- `main.js` has backward-compat `escapeHtml` wrapper

## Backend Issues
- Bare `except Exception:` blocks without logging in several views and services
- `news.date` is `CharField` instead of `DateField`
- `admin_index` view calls `Model.objects.count()` directly (layer violation)
- `api_views.py` calls `ProductService._mock_products()` (private method access)
- `settings.py` has insecure default SECRET_KEY for production
- `admin.js` has debug `console.log` statements left in

## No Test Suite
- No unit tests, integration tests, or E2E tests exist
- Be cautious with refactors — verify manually
