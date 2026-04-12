# API Patterns

## URL Structure
```
# Frontend (SSR HTML)
/                    → Home page
/products/:id/       → Product detail
/news/:id/           → News detail
/p/:slug/            → Static pages

# API (JSON)
/api/products        → Product list (paginated)
/api/products/:id    → Product detail
/api/news            → News list (paginated)
/api/news/:id        → News detail
/api/site            → Site configuration
/api/newsletter/subscribe → Newsletter signup

# Admin (Basic Auth required)
/admin/              → Admin dashboard
/admin/products/     → CRUD products
/admin/news/         → CRUD news
# ... etc

# SEO
/sitemap.xml         → Dynamic sitemap
/robots.txt          → Robots file
```

## Response Format (paginated lists)
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "limit": 8,
  "totalPages": 13
}
```

## Response Format (single item)
```json
{
  "id": 1,
  "name": "Product Name",
  "slug": "product-name",
  "price": 150000,
  "createdAt": "2025-01-01T00:00:00Z"
}
```

## Conventions
- Field names in API responses use **camelCase** (converted from snake_case by `to_dict()`)
- Pagination: `page` and `limit` query params
- Filtering: query params matching field names (`category`, `search`, `sort`)
- Sorting: `sort` param with values like `newest`, `price_asc`, `price_desc`, `bestseller`
- All URLs defined in `api/urls.py`
