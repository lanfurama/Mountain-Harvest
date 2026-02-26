"""Product controller."""
from pathlib import Path
from starlette.responses import JSONResponse, RedirectResponse, HTMLResponse
from api.services.product_service import ProductService
from api.views.product_views import ProductViews

_index_html_cache = None


def _get_index_html():
    """Get index.html content, cached."""
    global _index_html_cache
    if _index_html_cache is not None:
        return _index_html_cache
    for path in [Path(__file__).resolve().parent.parent.parent / "public" / "index.html", Path.cwd() / "public" / "index.html"]:
        if path.exists():
            _index_html_cache = path.read_text(encoding="utf-8")
            return _index_html_cache
    return None


class ProductController:
    """Controller for Product routes."""
    
    @staticmethod
    async def get_products(
        category: str = None,
        price: str = None,
        standard: str = None,
        search: str = None,
        sort: str = "newest",
        page: int = 1,
        limit: int = 8,
    ):
        """Get products with filters, sorting, and pagination."""
        page = max(1, page)
        limit = max(1, min(100, limit))
        items, total, total_pages = await ProductService.get_products_with_mock_fallback(
            category=category,
            price=price,
            standard=standard,
            search=search,
            sort=sort,
            page=page,
            limit=limit,
        )
        return JSONResponse({
            "items": items,
            "total": total,
            "page": page,
            "limit": limit,
            "totalPages": total_pages,
        })
    
    @staticmethod
    async def get_product_detail(id: int):
        """Get product by ID."""
        product = await ProductService.get_product(id)
        if not product:
            mock_products = ProductService._mock_products()
            product = next((x for x in mock_products if x["id"] == id), None)
            if not product:
                return JSONResponse({"error": "Not found"}, status_code=404)
        return JSONResponse(product)

    @staticmethod
    async def render_product_page(req, id: int):
        """Render product detail page (SSR)."""
        product = await ProductService.get_product(id)
        if not product:
            return RedirectResponse("/", status_code=302)
        html_content = _get_index_html()
        if not html_content:
            return RedirectResponse("/", status_code=302)
        current_url = str(req.url)
        html_content = ProductViews.render_detail(html_content, product, current_url)
        response = HTMLResponse(content=html_content)
        response.headers["X-Server-Rendered"] = "true"
        response.headers["Cache-Control"] = "public, max-age=300, stale-while-revalidate=600"
        return response
