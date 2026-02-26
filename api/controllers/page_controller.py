"""Page controller."""
from pathlib import Path
from starlette.responses import RedirectResponse, HTMLResponse
from api.repositories.page_repository import PageRepository
from api.views.page_views import PageViews

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


class PageController:
    """Controller for static pages."""

    @staticmethod
    async def render_page(req, slug: str):
        """Render static page by slug."""
        page = await PageRepository.get_by_slug(slug)
        if not page:
            return RedirectResponse("/", status_code=302)
        html_content = _get_index_html()
        if not html_content:
            return RedirectResponse("/", status_code=302)
        current_url = str(req.url)
        html_content = PageViews.render_detail(html_content, page, current_url)
        response = HTMLResponse(content=html_content)
        response.headers["X-Server-Rendered"] = "true"
        response.headers["Cache-Control"] = "public, max-age=300, stale-while-revalidate=600"
        return response
