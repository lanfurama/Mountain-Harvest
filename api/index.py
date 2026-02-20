"""FastHTML CMS Backend for Mountain Harvest."""
import os
from pathlib import Path
from starlette.responses import FileResponse, JSONResponse
from fasthtml.common import *

from api.db import init_db
from api.middleware.auth import admin_beforeware
from api.controllers.product_controller import ProductController
from api.controllers.news_controller import NewsController
from api.controllers.site_controller import SiteController
from api.controllers.admin_controller import AdminController

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


# Frontend routes
@rt("/")
async def index(req):
    """Serve frontend index.html with dynamic SEO and content for news."""
    result = await NewsController.render_index_with_news(req)
    if result:
        return result
    
    idx = PUBLIC_DIR / "index.html"
    try:
        if not idx.exists():
            return Div("Mountain Harvest - Add public/index.html")
    except Exception:
        pass
    
    return FileResponse(idx)


# API routes
@rt("/api/products")
async def api_products(
    category: str = None,
    price: str = None,
    standard: str = None,
    sort: str = "newest",
    page: int = 1,
    limit: int = 8,
):
    """Get products API."""
    return await ProductController.get_products(
        category=category,
        price=price,
        standard=standard,
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


@rt("/news/{id:int}")
async def news_detail_page(req, id: int):
    """Serve news detail page."""
    return await NewsController.render_news_page(req, id)


@rt("/api/site")
async def api_site():
    """Get site configuration API."""
    return await SiteController.get_site()


# Admin routes
@rt("/admin")
async def admin_index(req):
    """Admin dashboard."""
    return await AdminController.index(req)


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
