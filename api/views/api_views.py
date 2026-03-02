"""API views."""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from api.services.product_service import ProductService
from api.services.news_service import NewsService
from api.repositories.hero_repository import HeroRepository
from api.repositories.category_repository import CategoryRepository
from api.repositories.site_config_repository import SiteConfigRepository
from api.repositories.page_repository import PageRepository
import json


def api_products(request):
    """Get products API."""
    category = request.GET.get('category')
    price = request.GET.get('price')
    standard = request.GET.get('standard')
    search = request.GET.get('search')
    sort = request.GET.get('sort', 'newest')
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1
    try:
        limit = int(request.GET.get('limit', 8))
    except ValueError:
        limit = 8
    
    page = max(1, page)
    limit = max(1, min(100, limit))
    items, total, total_pages = ProductService.get_products_with_mock_fallback(
        category=category,
        price=price,
        standard=standard,
        search=search,
        sort=sort,
        page=page,
        limit=limit,
    )
    return JsonResponse({
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "totalPages": total_pages,
    })


def api_product_detail(request, id):
    """Get product detail API."""
    product = ProductService.get_product(id)
    if not product:
        mock_products = ProductService._mock_products()
        product = next((x for x in mock_products if x["id"] == id), None)
        if not product:
            return JsonResponse({"error": "Not found"}, status=404)
    return JsonResponse(product)


def api_news(request):
    """Get news API."""
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1
    try:
        limit = int(request.GET.get('limit', 6))
    except ValueError:
        limit = 6
    
    items, total, total_pages = NewsService.get_news_with_mock_fallback(page=page, limit=limit)
    return JsonResponse({
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "totalPages": total_pages,
    })


def api_news_detail(request, id):
    """Get news detail API."""
    news = NewsService.get_news_by_id_with_mock_fallback(id)
    if not news:
        return JsonResponse({"error": "Not found"}, status=404)
    return JsonResponse(news)


def api_news_related(request, id):
    """Get related news articles API."""
    try:
        limit = int(request.GET.get('limit', 3))
    except ValueError:
        limit = 3
    limit = max(1, min(10, limit))
    
    items = NewsService.get_related_news(id=id, limit=limit)
    return JsonResponse({"items": items})


def api_site(request):
    """Get site configuration API."""
    def _cfg(config, k):
        """Get config value as dict."""
        v = config.get(k)
        if v is None:
            return {}
        if isinstance(v, dict):
            return v
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}
    
    try:
        hero = HeroRepository.get()
        brochures = CategoryRepository.get_category_brochures()
        config_rows = SiteConfigRepository.get_all()
        
        hero_dict = hero.to_dict() if hero else {}
        
        return JsonResponse({
            "hero": {
                "promo": hero_dict.get("promo", "Summer Sale"),
                "title": hero_dict.get("title", "Fresh Produce For Green Living"),
                "subtitle": hero_dict.get("subtitle", "Up to 20% off on vegetables and fruits this week."),
                "image": hero_dict.get("image", ""),
                "buttonText": hero_dict.get("buttonText", "Shop Now"),
            },
            "categories": [cat.name for cat in CategoryRepository.get_all()],
            "brochures": [
                {"slug": b["slug"], "title": b["title"], "desc": b["desc"], "image": b["image"], "buttonText": b["button_text"]}
                for b in brochures
            ],
            "brand": _cfg(config_rows, "brand"),
            "header": _cfg(config_rows, "brand") or _cfg(config_rows, "header"),
            "topbar": _cfg(config_rows, "topbar"),
            "footer": _cfg(config_rows, "footer"),
        })
    except Exception:
        return JsonResponse({
            "hero": {
                "promo": "Summer Sale",
                "title": "Fresh Produce For Green Living",
                "subtitle": "Up to 20% off.",
                "image": "https://images.unsplash.com/photo-1542838132-92c53300491e?w=1920&q=80",
                "buttonText": "Shop Now"
            },
            "categories": ["Rau củ quả", "Hạt & Ngũ cốc", "Gia dụng"],
            "brochures": [],
            "topbar": {"freeShipping": "Free shipping for orders over 500k", "hotline": "1900 1234", "support": "Customer Support"},
            "footer": {"address": "123 Đường Mây Núi, Đà Lạt", "phone": "1900 1234", "email": "cskh@mountainharvest.vn"},
        })


def api_pages(request):
    """Get public pages list (slug, title) for footer links."""
    pages = PageRepository.get_all()
    items = [{"slug": p["slug"], "title": p.get("title", "")} for p in pages]
    return JsonResponse({"items": items})


@require_http_methods(["POST"])
def api_newsletter_subscribe(request):
    """Subscribe email to newsletter."""
    from api.models.newsletter import NewsletterSubscriber
    import json as json_lib
    
    try:
        if request.content_type and 'application/json' in request.content_type:
            body = json_lib.loads(request.body)
        else:
            body = request.POST
        
        email = (body.get("email") or "").strip().lower()
        if not email or "@" not in email:
            return JsonResponse({"ok": False, "error": "Email không hợp lệ"}, status=400)
        
        NewsletterSubscriber.objects.get_or_create(email=email)
        return JsonResponse({"ok": True, "message": "Đăng ký thành công!"})
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=500)
