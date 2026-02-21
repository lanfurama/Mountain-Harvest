"""News controller."""
from typing import Optional
from starlette.responses import JSONResponse, RedirectResponse, HTMLResponse
from pathlib import Path
from api.services.news_service import NewsService
from api.views.news_views import NewsViews

_index_html_cache = None


def _get_index_html() -> Optional[str]:
    """Get index.html content, cached in memory after first read."""
    global _index_html_cache
    if _index_html_cache is not None:
        return _index_html_cache
    possible_paths = [
        Path(__file__).resolve().parent.parent.parent / "public" / "index.html",
        Path.cwd() / "public" / "index.html",
    ]
    for path in possible_paths:
        try:
            if path.exists() and path.is_file():
                _index_html_cache = path.read_text(encoding="utf-8")
                return _index_html_cache
        except (FileNotFoundError, OSError):
            continue
    return None


class NewsController:
    """Controller for News routes."""
    
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
    PUBLIC_DIR = PROJECT_ROOT / "public"
    
    @staticmethod
    async def get_news(page: int = 1, limit: int = 6):
        """Get news with pagination."""
        page = max(1, page)
        limit = max(1, min(100, limit))
        items, total, total_pages = await NewsService.get_news_with_mock_fallback(page=page, limit=limit)
        return JSONResponse({
            "items": items,
            "total": total,
            "page": page,
            "limit": limit,
            "totalPages": total_pages,
        })
    
    @staticmethod
    async def get_news_detail(id: int):
        """Get news by ID."""
        news = await NewsService.get_news_by_id_with_mock_fallback(id)
        if not news:
            return JSONResponse({"error": "Not found"}, status_code=404)
        return JSONResponse(news)
    
    @staticmethod
    async def render_news_page(req, id: int):
        """Render news detail page."""
        try:
            news = await NewsService.get_news_by_id_with_mock_fallback(id)
            if not news:
                return RedirectResponse("/", status_code=302)

            html_content = _get_index_html()
            if html_content:
                current_url = str(req.url)
                html_content = NewsViews.render_detail(html_content, news, current_url)
                return HTMLResponse(content=html_content)
            return RedirectResponse("/?news=" + str(id), status_code=302)
        except Exception:
            return RedirectResponse("/", status_code=302)
    
    @staticmethod
    async def render_index_with_news(req):
        """Render index page with optional news parameter."""
        news_id = req.query_params.get("news")
        if not news_id:
            return None
        try:
            news_id_int = int(news_id)
            news = await NewsService.get_news_by_id_with_mock_fallback(news_id_int)
            if not news:
                return None
            html_content = _get_index_html()
            if html_content:
                current_url = str(req.url)
                html_content = NewsViews.render_detail(html_content, news, current_url)
                return HTMLResponse(content=html_content)
        except (ValueError, Exception):
            pass
        return None
