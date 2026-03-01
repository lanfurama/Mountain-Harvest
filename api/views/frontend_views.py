"""Frontend views."""
from pathlib import Path
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from api.services.product_service import ProductService
from api.services.news_service import NewsService
from api.views.home_views import HomeViews
from api.views.news_views import NewsViews, normalize_content_headers
from api.views.product_views import ProductViews
from api.views.page_views import PageViews
from api.repositories.page_repository import PageRepository
from urllib.parse import urlparse, urlunparse

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


def normalize_url(url: str) -> str:
    """Normalize URL: convert 127.0.0.1 to localhost for consistency."""
    if not url:
        return url
    parsed = urlparse(url)
    netloc = parsed.netloc
    if netloc.startswith('127.0.0.1'):
        netloc = netloc.replace('127.0.0.1', 'localhost', 1)
    return urlunparse((
        parsed.scheme,
        netloc,
        parsed.path,
        parsed.params,
        parsed.query,
        parsed.fragment
    ))


def index(request):
    """Serve frontend index.html with server-side rendered content."""
    # Check for news query parameter
    news_id = request.GET.get("news")
    if news_id:
        try:
            news_id_int = int(news_id)
            news = NewsService.get_news_by_id_with_mock_fallback(news_id_int)
            if news:
                html_content = _get_index_html()
                if html_content:
                    current_url = normalize_url(request.build_absolute_uri())
                    html_content = NewsViews.render_detail(html_content, news, current_url)
                    response = HttpResponse(html_content, content_type='text/html; charset=utf-8')
                    response['X-Server-Rendered'] = 'true'
                    return response
        except (ValueError, Exception):
            pass

    # Load base HTML template
    html_template = _get_index_html()
    if not html_template:
        return HttpResponse("Mountain Harvest - Add public/index.html")

    # Read filters and pagination from query params
    category = request.GET.get("category")
    price = request.GET.get("price")
    standard = request.GET.get("standard")
    search = request.GET.get("search")
    sort = request.GET.get("sort", "newest")

    try:
        page = int(request.GET.get("page", 1))
    except ValueError:
        page = 1
    try:
        news_page = int(request.GET.get("news_page", 1))
    except ValueError:
        news_page = 1

    # Get products and news data server-side
    products_items, products_total, products_total_pages = ProductService.get_products_with_mock_fallback(
        category=category,
        price=price,
        standard=standard,
        search=search,
        sort=sort,
        page=page,
        limit=8,
    )
    news_items, news_total, news_total_pages = NewsService.get_news_with_mock_fallback(
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
    return HttpResponse(rendered_html, content_type='text/html; charset=utf-8')


def news_detail(request, id):
    """Serve news detail page - Server-side rendered."""
    try:
        news = NewsService.get_news_by_id_with_mock_fallback(id)
        if not news:
            # Log for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"News with id={id} not found")
            # Return 404 instead of redirect
            from django.http import Http404
            raise Http404(f"News with id={id} not found")

        html_content = _get_index_html()
        if not html_content:
            return HttpResponseRedirect("/?news=" + str(id))
        
        current_url = normalize_url(request.build_absolute_uri())
        html_content = NewsViews.render_detail(html_content, news, current_url)
        response = HttpResponse(html_content, content_type='text/html')
        response['X-Server-Rendered'] = 'true'
        response['Cache-Control'] = 'public, max-age=300, stale-while-revalidate=600'
        return response
    except Exception as e:
        # Log exception for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error rendering news detail for id={id}: {e}", exc_info=True)
        return HttpResponseRedirect("/")


def product_detail(request, id):
    """Serve product detail page - Server-side rendered."""
    try:
        product = ProductService.get_product(id)
        if not product:
            mock_products = ProductService._mock_products()
            product = next((x for x in mock_products if x["id"] == id), None)
            if not product:
                return HttpResponseRedirect("/")

        html_content = _get_index_html()
        if html_content:
            current_url = normalize_url(request.build_absolute_uri())
            html_content = ProductViews.render_detail(html_content, product, current_url)
            response = HttpResponse(html_content, content_type='text/html; charset=utf-8')
            response['X-Server-Rendered'] = 'true'
            response['Cache-Control'] = 'public, max-age=300, stale-while-revalidate=600'
            return response
        return HttpResponseRedirect("/")
    except Exception:
        return HttpResponseRedirect("/")


def page_detail(request, slug):
    """Serve static page by slug."""
    try:
        page = PageRepository.get_by_slug(slug)
        if not page:
            return HttpResponseRedirect("/")

        html_content = _get_index_html()
        if html_content:
            current_url = normalize_url(request.build_absolute_uri())
            html_content = PageViews.render_detail(html_content, page, current_url)
            response = HttpResponse(html_content, content_type='text/html; charset=utf-8')
            response['X-Server-Rendered'] = 'true'
            response['Cache-Control'] = 'public, max-age=300, stale-while-revalidate=600'
            return response
        return HttpResponseRedirect("/")
    except Exception:
        return HttpResponseRedirect("/")
