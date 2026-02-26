"""FastHTML CMS Backend for Mountain Harvest."""
import os
from pathlib import Path
from starlette.responses import FileResponse, JSONResponse, HTMLResponse
from fasthtml.common import *

from api.db import init_db
from api.middleware.auth import admin_beforeware
from api.controllers.product_controller import ProductController
from api.controllers.news_controller import NewsController, _get_index_html
from api.controllers.site_controller import SiteController
from api.controllers.admin_controller import AdminController
from api.controllers.seo_controller import generate_sitemap, generate_robots
from api.controllers.page_controller import PageController
from api.services.product_service import ProductService
from api.services.news_service import NewsService
from api.views.home_views import HomeViews

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PUBLIC_DIR = PROJECT_ROOT / "public"
STATIC_PATH = str(PUBLIC_DIR)

app = FastHTML(
    pico=False,
    before=admin_beforeware,
    static_path=STATIC_PATH if PUBLIC_DIR.exists() else None,
    hdrs=(
        Link(rel="stylesheet", href="https://cdn.tailwindcss.com"),
        Link(rel="stylesheet", href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"),
    ),
)
rt = app.route


# Favicon
@rt("/favicon.svg")
async def serve_favicon():
    file_path = PUBLIC_DIR / "favicon.svg"
    if file_path.exists():
        return FileResponse(file_path, media_type="image/svg+xml")
    return JSONResponse({"error": "Not found"}, status_code=404)


# Serve static files from subdirectories
@rt("/css/{filename:str}")
async def serve_css(filename: str):
    """Serve CSS files."""
    file_path = PUBLIC_DIR / "css" / filename
    if file_path.exists() and file_path.suffix == ".css":
        return FileResponse(file_path, media_type="text/css")
    return JSONResponse({"error": "Not found"}, status_code=404)


@rt("/js/{filename:str}")
async def serve_js(filename: str):
    """Serve JavaScript files."""
    file_path = PUBLIC_DIR / "js" / filename
    if file_path.exists() and file_path.suffix == ".js":
        return FileResponse(file_path, media_type="application/javascript")
    return JSONResponse({"error": "Not found"}, status_code=404)


@rt("/components/{filename:str}")
async def serve_components(filename: str):
    """Serve component HTML files."""
    file_path = PUBLIC_DIR / "components" / filename
    if file_path.exists() and file_path.suffix == ".html":
        return FileResponse(file_path, media_type="text/html")
    return JSONResponse({"error": "Not found"}, status_code=404)


# News detail page route - MUST be defined before root route to ensure it's matched first
@rt("/news/{id:int}")
async def news_detail_page(req, id: int):
    """Serve news detail page - Server-side rendered."""
    # Ensure this route is matched and not served as static file
    response = await NewsController.render_news_page(req, id)
    # Add header to indicate server-side rendering
    if hasattr(response, 'headers'):
        response.headers['X-Server-Rendered'] = 'true'
        response.headers['Cache-Control'] = 'public, max-age=300, stale-while-revalidate=600'
    return response


# SEO
@rt("/sitemap.xml")
async def sitemap(req):
    """Serve sitemap.xml."""
    return await generate_sitemap(req)


@rt("/robots.txt")
async def robots(req):
    """Serve robots.txt."""
    return generate_robots(req)


# Static page route - SSR
@rt("/p/{slug:str}")
async def page_detail(req, slug: str):
    """Serve static page by slug."""
    return await PageController.render_page(req, slug)


# Product detail page route - SSR
@rt("/products/{id:int}")
async def product_detail_page(req, id: int):
    """Serve product detail page - Server-side rendered."""
    return await ProductController.render_product_page(req, id)


# Frontend routes
@rt("/")
async def index(req):
    """Serve frontend index.html with server-side rendered content."""
    # If there is an explicit news query, reuse news detail SSR logic
    result = await NewsController.render_index_with_news(req)
    if result:
        return result

    # Load base HTML template
    html_template = _get_index_html()
    if not html_template:
        idx = PUBLIC_DIR / "index.html"
        try:
            if not idx.exists():
                return Div("Mountain Harvest - Add public/index.html")
        except Exception:
            pass
        return FileResponse(idx)

    # Read filters and pagination from query params
    qp = req.query_params
    category = qp.get("category") or None
    price = qp.get("price") or None
    standard = qp.get("standard") or None
    search = qp.get("search") or None
    sort = qp.get("sort") or "newest"

    try:
        page = int(qp.get("page") or 1)
    except ValueError:
        page = 1
    try:
        news_page = int(qp.get("news_page") or 1)
    except ValueError:
        news_page = 1

    # Get products and news data server-side
    products_items, products_total, products_total_pages = await ProductService.get_products_with_mock_fallback(
        category=category,
        price=price,
        standard=standard,
        search=search,
        sort=sort,
        page=page,
        limit=8,
    )
    news_items, news_total, news_total_pages = await NewsService.get_news_with_mock_fallback(
        page=news_page,
        limit=6,
    )

    products_page = {
        "items": products_items,
        "total": products_total,
        "page": page,
        "total_pages": products_total_pages,
    }
    news_page_data = {
        "items": news_items,
        "total": news_total,
        "page": news_page,
        "total_pages": news_total_pages,
    }
    filters = {
        "category": category or "",
        "price": price or "",
        "standard": standard or "",
        "search": search or "",
        "sort": sort or "newest",
    }

    rendered_html = HomeViews.render_home(
        base_html=html_template,
        products_page=products_page,
        news_page=news_page_data,
        filters=filters,
        news_page_param="news_page",
    )
    return HTMLResponse(content=rendered_html)


# API routes
@rt("/api/products")
async def api_products(
    category: str = None,
    price: str = None,
    standard: str = None,
    search: str = None,
    sort: str = "newest",
    page: int = 1,
    limit: int = 8,
):
    """Get products API."""
    return await ProductController.get_products(
        category=category,
        price=price,
        standard=standard,
        search=search,
        sort=sort,
        page=page,
        limit=limit,
    )


@rt("/api/products/{id:int}")
async def api_product_detail(id: int):
    """Get product detail API."""
    return await ProductController.get_product_detail(id)


@rt("/api/news")
async def api_news(page: int = 1, limit: int = 6):
    """Get news API."""
    return await NewsController.get_news(page=page, limit=limit)


@rt("/api/news/{id:int}")
async def api_news_one(id: int):
    """Get news detail API."""
    return await NewsController.get_news_detail(id)


@rt("/api/site")
async def api_site():
    """Get site configuration API."""
    return await SiteController.get_site()


@rt("/api/pages")
async def api_pages():
    """Get public pages list (slug, title) for footer links."""
    from api.repositories.page_repository import PageRepository
    pages = await PageRepository.get_all()
    items = [{"slug": p["slug"], "title": p.get("title", "")} for p in pages]
    return JSONResponse({"items": items})


@rt("/api/newsletter/subscribe")
async def api_newsletter_subscribe(req):
    """Subscribe email to newsletter."""
    from api.db import get_conn
    if req.method != "POST":
        return JSONResponse({"ok": False, "error": "Method not allowed"}, status_code=405)
    try:
        body = await req.json() if req.headers.get("content-type", "").startswith("application/json") else {}
        email = (body.get("email") or "").strip().lower()
        if not email or "@" not in email:
            return JSONResponse({"ok": False, "error": "Email không hợp lệ"}, status_code=400)
        async with get_conn() as conn:
            if not conn:
                return JSONResponse({"ok": False, "error": "Hệ thống tạm thời không khả dụng"}, status_code=503)
            await conn.execute(
                "INSERT INTO newsletter_subscribers (email) VALUES ($1) ON CONFLICT (email) DO NOTHING",
                email,
            )
        return JSONResponse({"ok": True, "message": "Đăng ký thành công!"})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


# Admin routes
@rt("/admin")
async def admin_index(req):
    """Admin dashboard."""
    return await AdminController.index(req)


@rt("/admin/categories")
async def admin_categories(req):
    """Admin categories list."""
    return await AdminController.categories(req)


@rt("/admin/categories/add")
async def admin_category_add(req):
    """Add category."""
    return await AdminController.category_add(req)


@rt("/admin/categories/{id:int}/edit")
async def admin_category_edit(req, id: int):
    """Edit category."""
    return await AdminController.category_edit(req, id)


@rt("/admin/categories/{id:int}")
async def admin_category_update(req, id: int):
    """Update category."""
    return await AdminController.category_update(req, id)


@rt("/admin/categories/{id:int}/delete")
async def admin_category_delete(req, id: int):
    """Delete category."""
    return await AdminController.category_delete(req, id)


@rt("/admin/products")
async def admin_products(req):
    """Admin products list."""
    return await AdminController.products(req)


@rt("/admin/products/new")
async def admin_product_new(req):
    """Create new product."""
    return await AdminController.product_new(req)


@rt("/admin/products/{id:int}/edit")
async def admin_product_edit(req, id: int):
    """Edit product."""
    return await AdminController.product_edit(req, id)


@rt("/admin/products/{id:int}")
async def admin_product_update(req, id: int):
    """Update product."""
    return await AdminController.product_update(req, id)


@rt("/admin/products/{id:int}/delete")
async def admin_product_delete(req, id: int):
    """Delete product."""
    return await AdminController.product_delete(req, id)


@rt("/admin/news")
async def admin_news(req):
    """Admin news list."""
    return await AdminController.news(req)


@rt("/admin/news/add")
async def admin_news_add(req):
    """Add news."""
    return await AdminController.news_add(req)


@rt("/admin/news/{id:int}/edit")
async def admin_news_edit(req, id: int):
    """Edit news."""
    return await AdminController.news_edit(req, id)


@rt("/admin/news/{id:int}")
async def admin_news_update(req, id: int):
    """Update news."""
    return await AdminController.news_update(req, id)


@rt("/admin/news/{id:int}/delete")
async def admin_news_delete(req, id: int):
    """Delete news."""
    return await AdminController.news_delete(req, id)


@rt("/admin/pages")
async def admin_pages(req):
    """Admin pages list."""
    return await AdminController.pages(req)


@rt("/admin/pages/add")
async def admin_page_add(req):
    """Add page."""
    return await AdminController.page_add(req)


@rt("/admin/pages/{id:int}/edit")
async def admin_page_edit(req, id: int):
    """Edit page."""
    return await AdminController.page_edit(req, id)


@rt("/admin/pages/{id:int}")
async def admin_page_update(req, id: int):
    """Update page."""
    return await AdminController.page_update(req, id)


@rt("/admin/pages/{id:int}/delete")
async def admin_page_delete(req, id: int):
    """Delete page."""
    return await AdminController.page_delete(req, id)


@rt("/admin/hero")
async def admin_hero(req):
    """Admin hero."""
    return await AdminController.hero(req)


@rt("/admin/hero/save")
async def admin_hero_save(req):
    """Save hero."""
    return await AdminController.hero_save(req)


@rt("/admin/site")
async def admin_site(req):
    """Admin site config."""
    return await AdminController.site(req)


@rt("/admin/site/brand")
async def admin_site_brand(req):
    """Update brand config."""
    return await AdminController.site_brand(req)


@rt("/admin/site/topbar")
async def admin_site_topbar(req):
    """Update topbar config."""
    return await AdminController.site_topbar(req)


@rt("/admin/site/footer")
async def admin_site_footer(req):
    """Update footer config."""
    return await AdminController.site_footer(req)


@rt("/admin/site/brochure/{slug:str}")
async def admin_site_brochure(req, slug: str):
    """Update brochure."""
    return await AdminController.site_brochure(req, slug)


# Startup: init DB
@app.on_event("startup")
async def startup():
    await init_db()


# Vercel: chỉ export app (ASGI). Không export handler để tránh runtime coi là BaseHTTPRequestHandler.
if __name__ == "__main__" or os.getenv("VERCEL") != "1":
    serve()
