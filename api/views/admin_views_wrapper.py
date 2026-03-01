"""Admin views wrapper - uses existing AdminViews."""
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from api.views.admin_views import AdminViews
from api.repositories.product_repository import ProductRepository
from api.repositories.news_repository import NewsRepository
from api.repositories.hero_repository import HeroRepository
from api.repositories.site_config_repository import SiteConfigRepository
from api.repositories.category_repository import CategoryRepository
from api.repositories.page_repository import PageRepository
from api.models.product import Product
from api.models.news import News
from api.models.category import Category
from api.models.page import Page
import json


class MockRequest:
    """Mock request object for AdminViews.layout() compatibility."""
    def __init__(self, django_request):
        self.url = type('obj', (object,), {'path': django_request.path})()


def _render_html(html_obj):
    """Convert FastHTML Html object to string with proper UTF-8 encoding."""
    # FastHTML Html object returns a tuple (doctype, html_content)
    if isinstance(html_obj, tuple) and len(html_obj) == 2:
        html_str = str(html_obj[0]) + str(html_obj[1])
    else:
        html_str = str(html_obj)
    
    # Python 3 strings are already Unicode, but ensure we have proper encoding
    # Ensure UTF-8 encoding is set in HTML meta tag (AdminViews.layout already adds it, but double-check)
    html_lower = html_str.lower()
    if 'charset=' not in html_lower and 'charset=' not in html_str:
        # Insert charset meta tag after <head> or at the beginning
        if '<head>' in html_str:
            html_str = html_str.replace('<head>', '<head>\n    <meta charset="UTF-8">', 1)
        elif '<html>' in html_str:
            html_str = html_str.replace('<html>', '<html>\n<head>\n    <meta charset="UTF-8">\n</head>', 1)
    
    return html_str


def _build_query_string(params: dict, updates: dict = None) -> str:
    """Build query string."""
    from urllib.parse import urlencode
    merged = {**params}
    if updates:
        merged.update(updates)
    parts = [f"{k}={v}" for k, v in merged.items() if v]
    return "?" + urlencode(merged) if parts else ""


def admin_index(request):
    """Admin dashboard."""
    counts = {
        "products": Product.objects.count(),
        "news": News.objects.count(),
        "categories": Category.objects.count(),
        "pages": Page.objects.count(),
    }
    
    # Create content for dashboard
    stats = [
        (counts["products"], "fa-box", "Sản phẩm", "/admin/products", "bg-gradient-to-br from-blue-500 to-blue-600", "text-blue-600"),
        (counts["news"], "fa-newspaper", "Tin tức", "/admin/news", "bg-gradient-to-br from-purple-500 to-purple-600", "text-purple-600"),
        (counts["categories"], "fa-folder", "Danh mục", "/admin/categories", "bg-gradient-to-br from-green-500 to-green-600", "text-green-600"),
        (counts["pages"], "fa-file-alt", "Trang", "/admin/pages", "bg-gradient-to-br from-orange-500 to-orange-600", "text-orange-600"),
    ]
    
    from fasthtml.common import Div, A, Span, I, H2, Button
    cards = []
    for n, icon, label, href, icon_bg, icon_color in stats:
        cards.append(
            A(href=href, cls="group block p-4 rounded border border-gray-200 bg-white hover:shadow-md hover:border-[#2F5233]/30 transition-all duration-300 transform hover:-translate-y-0.5")(
                Div(cls="flex items-center justify-between mb-3")(
                    Div(
                        Div(cls="text-2xl font-bold text-gray-900 mb-1")(str(n)),
                        Div(cls="text-sm font-medium text-gray-600")(label),
                    ),
                    Div(cls=f"w-12 h-12 rounded {icon_bg} flex items-center justify-center shadow-md group-hover:scale-110 transition-transform")(
                        I(cls=f"fas {icon} text-white text-lg"),
                    ),
                ),
                Div(cls="flex items-center gap-2 text-xs text-gray-500")(
                    I(cls="fas fa-arrow-right text-[#2F5233] group-hover:translate-x-1 transition-transform"),
                    Span("Xem chi tiết", cls="font-medium"),
                ),
            )
        )
    
    quick_actions = Div(cls="mt-5")(
        H2("Thao tác nhanh", cls="text-lg font-bold text-gray-900 mb-3 flex items-center gap-2")(
            I(cls="fas fa-bolt text-[#E85D04]"),
            Span("Thao tác nhanh"),
        ),
        Div(cls="grid grid-cols-1 md:grid-cols-3 gap-3")(
            A(
                href="/admin/products/new",
                cls="group flex items-center gap-3 p-3 rounded bg-gradient-to-r from-[#E85D04] to-[#c75003] text-white hover:shadow-lg transition-all duration-300 transform hover:scale-105"
            )(
                Div(cls="w-10 h-10 rounded bg-white/20 flex items-center justify-center")(
                    I(cls="fas fa-plus text-lg"),
                ),
                Div(
                    Span("Thêm sản phẩm", cls="font-semibold text-base block"),
                    Span("Tạo sản phẩm mới", cls="text-white/80 text-sm block"),
                ),
            ),
            A(
                href="/admin/news/add",
                cls="group flex items-center gap-3 p-3 rounded bg-gradient-to-r from-[#2F5233] to-[#1a331d] text-white hover:shadow-lg transition-all duration-300 transform hover:scale-105"
            )(
                Div(cls="w-10 h-10 rounded bg-white/20 flex items-center justify-center")(
                    I(cls="fas fa-newspaper text-lg"),
                ),
                Div(
                    Span("Thêm tin mới", cls="font-semibold text-base block"),
                    Span("Viết bài tin tức", cls="text-white/80 text-sm block"),
                ),
            ),
            A(
                href="/admin/categories/add",
                cls="group flex items-center gap-3 p-3 rounded bg-gradient-to-r from-blue-500 to-blue-600 text-white hover:shadow-lg transition-all duration-300 transform hover:scale-105"
            )(
                Div(cls="w-10 h-10 rounded bg-white/20 flex items-center justify-center")(
                    I(cls="fas fa-folder-plus text-lg"),
                ),
                Div(
                    Span("Thêm danh mục", cls="font-semibold text-base block"),
                    Span("Tạo danh mục mới", cls="text-white/80 text-sm block"),
                ),
            ),
        ),
    )
    
    content = Div(cls="space-y-5")(
        Div(cls="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4")(*cards),
        quick_actions,
    )
    
    try:
        mock_req = MockRequest(request)
        html_obj = AdminViews.layout(mock_req, "Dashboard", content)
        html_str = _render_html(html_obj)
        response = HttpResponse(html_str, content_type='text/html; charset=utf-8')
        return response
    except Exception as e:
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        logger.error(f"Error rendering admin index: {e}\n{traceback.format_exc()}")
        return HttpResponse(f"Error: {e}<br><pre>{traceback.format_exc()}</pre>", content_type='text/html; charset=utf-8')


def admin_products(request):
    """Admin products list."""
    search = request.GET.get('search', '')
    category = request.GET.get('category', '')
    sort = request.GET.get('sort', 'newest')
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1
    
    items, total = ProductRepository.search(category=category, search=search, sort=sort, page=page, per_page=10)
    total_pages = max(1, (total + 9) // 10)
    
    # Render products list using AdminViews
    from fasthtml.common import Div, Table, Thead, Tbody, Tr, Th, Td, A, Button, Input, Select, Option, Form, I, Span
    from urllib.parse import urlencode
    
    # Build table rows
    rows = []
    for item in items:
        item_id = item.get("id")
        if item_id is None:
            continue
        rows.append(
            Tr(cls="hover:bg-gray-50 transition")(
                Td(str(item_id), cls="px-4 py-3 text-sm text-gray-700"),
                Td(
                    A(href=f"/admin/products/{item_id}/edit", cls="font-medium text-[#2F5233] hover:underline")(
                        (item.get("name", "") or "")[:50] + ("..." if len(item.get("name", "") or "") > 50 else "")
                    )
                ),
                Td(item.get("category", ""), cls="px-4 py-3 text-sm text-gray-600"),
                Td(f"{item.get('price', 0):,}đ", cls="px-4 py-3 text-sm font-medium text-gray-900"),
                Td(
                    A(href=f"/admin/products/{item_id}/edit", cls="px-2 py-1 text-xs rounded bg-blue-100 text-blue-700 hover:bg-blue-200 transition")("Sửa"),
                    " ",
                    Button(
                        type="button",
                        onclick=f"confirmDelete({item_id}, '/admin/products/{item_id}/delete')",
                        cls="px-2 py-1 text-xs rounded bg-red-100 text-red-700 hover:bg-red-200 transition"
                    )("Xóa"),
                    cls="px-4 py-3 text-sm space-x-2"
                ),
            )
        )
    
    # Filters
    filters = Form(method="get", cls="mb-4 flex gap-2 flex-wrap")(
        Input(
            type="text",
            name="search",
            value=search,
            placeholder="Tìm kiếm...",
            cls="px-3 py-2 border border-gray-300 rounded text-sm flex-1 min-w-[200px]"
        ),
        Select(
            name="category",
            cls="px-3 py-2 border border-gray-300 rounded text-sm"
        )(
            *[Option(value="", selected=not category)("Tất cả danh mục")] +
            [Option(value=cat, selected=category==cat)(cat) for cat in ProductRepository.get_categories()]
        ),
        Select(
            name="sort",
            cls="px-3 py-2 border border-gray-300 rounded text-sm"
        )(
            Option(value="newest", selected=sort=="newest")("Mới nhất"),
            Option(value="oldest", selected=sort=="oldest")("Cũ nhất"),
            Option(value="name", selected=sort=="name")("Tên A-Z"),
        ),
        Button(
            type="submit",
            cls="px-4 py-2 bg-[#2F5233] text-white rounded hover:bg-[#1a331d] transition text-sm"
        )("Lọc"),
        A(
            href="/admin/products/new",
            cls="px-4 py-2 bg-[#E85D04] text-white rounded hover:bg-[#c75003] transition text-sm"
        )("+ Thêm mới"),
    )
    
    # Pagination
    pagination = Div(cls="mt-4 flex items-center justify-between")
    if total_pages > 1:
        pag_links = []
        for p in range(1, total_pages + 1):
            params = {"page": str(p)}
            if search:
                params["search"] = search
            if category:
                params["category"] = category
            if sort != "newest":
                params["sort"] = sort
            url = "/admin/products?" + urlencode(params)
            pag_links.append(
                A(
                    href=url,
                    cls=f"px-3 py-1 rounded text-sm {'bg-[#2F5233] text-white' if p == page else 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'}"
                )(str(p))
            )
        pagination = Div(cls="mt-4 flex items-center justify-between")(
            Div(cls="text-sm text-gray-600")(
                f"Hiển thị {(page-1)*10 + 1}-{min(page*10, total)} trong {total} sản phẩm"
            ),
            Div(cls="flex gap-1")(*pag_links),
        )
    
    content = Div(cls="space-y-4")(
        filters,
        Div(cls="bg-white rounded border border-gray-200 overflow-hidden")(
            Table(cls="w-full")(
                Thead(cls="bg-gray-50")(
                    Tr(
                        Th("ID", cls="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase"),
                        Th("Tên", cls="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase"),
                        Th("Danh mục", cls="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase"),
                        Th("Giá", cls="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase"),
                        Th("Thao tác", cls="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase"),
                    )
                ),
                Tbody(*rows) if rows else Tbody(Tr(Td("Không có sản phẩm nào", colspan=5, cls="px-4 py-8 text-center text-gray-500"))),
            )
        ),
        pagination,
    )
    
    mock_req = MockRequest(request)
    html_obj = AdminViews.layout(mock_req, "Quản lý Sản phẩm", content)
    html_str = _render_html(html_obj)
    response = HttpResponse(html_str, content_type='text/html; charset=utf-8')
    return response


def admin_product_new(request):
    """Create new product."""
    if request.method == 'POST':
        try:
            ProductRepository.create(
                name=request.POST.get('name', ''),
                category=request.POST.get('category', ''),
                price=int(request.POST.get('price', 0)),
                slug=request.POST.get('slug') or None,
                original_price=int(request.POST.get('original_price')) if request.POST.get('original_price') else None,
                unit=request.POST.get('unit') or None,
                image=request.POST.get('image') or None,
                description=request.POST.get('description') or None,
                tags=json.loads(request.POST.get('tags', '[]')) if request.POST.get('tags') else [],
                is_hot=request.POST.get('is_hot') == 'on',
                discount=request.POST.get('discount') or None,
                rating=float(request.POST.get('rating', 0)),
                reviews=int(request.POST.get('reviews', 0)),
                sort_order=int(request.POST.get('sort_order', 0)),
                meta_title=request.POST.get('meta_title') or None,
                meta_description=request.POST.get('meta_description') or None,
                h1_custom=request.POST.get('h1_custom') or None,
                h2_custom=request.POST.get('h2_custom') or None,
                h3_custom=request.POST.get('h3_custom') or None,
            )
            return HttpResponseRedirect('/admin/products')
        except Exception as e:
            # Render form with error
            pass
    
    # Render product form - simplified version
    from fasthtml.common import Div, Form, Input, Textarea, Select, Option, Label, Button
    categories = ProductRepository.get_categories()
    
    form = Form(method="post", cls="space-y-4")(
        Div(cls="grid grid-cols-1 md:grid-cols-2 gap-4")(
            Div(
                Label("Tên sản phẩm *", cls="block text-sm font-medium text-gray-700 mb-1"),
                Input(type="text", name="name", required=True, cls="w-full px-3 py-2 border border-gray-300 rounded"),
            ),
            Div(
                Label("Danh mục *", cls="block text-sm font-medium text-gray-700 mb-1"),
                Select(name="category", required=True, cls="w-full px-3 py-2 border border-gray-300 rounded")(
                    *[Option(value=cat)(cat) for cat in categories]
                ),
            ),
            Div(
                Label("Giá *", cls="block text-sm font-medium text-gray-700 mb-1"),
                Input(type="number", name="price", required=True, cls="w-full px-3 py-2 border border-gray-300 rounded"),
            ),
            Div(
                Label("Giá gốc", cls="block text-sm font-medium text-gray-700 mb-1"),
                Input(type="number", name="original_price", cls="w-full px-3 py-2 border border-gray-300 rounded"),
            ),
        ),
        Div(
            Label("Mô tả", cls="block text-sm font-medium text-gray-700 mb-1"),
            Textarea(name="description", rows=4, cls="w-full px-3 py-2 border border-gray-300 rounded"),
        ),
        Div(cls="flex gap-2")(
            Button(type="submit", cls="px-4 py-2 bg-[#2F5233] text-white rounded hover:bg-[#1a331d] transition")("Lưu"),
            A(href="/admin/products", cls="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition")("Hủy"),
        ),
    )
    
    content = Div(cls="space-y-4")(
        Div(cls="text-sm text-gray-600 mb-4")("Tạo sản phẩm mới"),
        form,
    )
    
    mock_req = MockRequest(request)
    html_obj = AdminViews.layout(mock_req, "Thêm Sản phẩm", content)
    html_str = _render_html(html_obj)
    response = HttpResponse(html_str, content_type='text/html; charset=utf-8')
    return response


def admin_product_edit(request, id):
    """Edit product."""
    product = ProductRepository.get_by_id_for_edit(id)
    if not product:
        return HttpResponseRedirect('/admin/products')
    
    if request.method == 'POST':
        try:
            ProductRepository.update(
                id=id,
                name=request.POST.get('name', ''),
                category=request.POST.get('category', ''),
                price=int(request.POST.get('price', 0)),
                slug=request.POST.get('slug') or None,
                original_price=int(request.POST.get('original_price')) if request.POST.get('original_price') else None,
                unit=request.POST.get('unit') or None,
                image=request.POST.get('image') or None,
                description=request.POST.get('description') or None,
                tags=json.loads(request.POST.get('tags', '[]')) if request.POST.get('tags') else [],
                is_hot=request.POST.get('is_hot') == 'on',
                discount=request.POST.get('discount') or None,
                rating=float(request.POST.get('rating', 0)),
                reviews=int(request.POST.get('reviews', 0)),
                sort_order=int(request.POST.get('sort_order', 0)),
                meta_title=request.POST.get('meta_title') or None,
                meta_description=request.POST.get('meta_description') or None,
                h1_custom=request.POST.get('h1_custom') or None,
                h2_custom=request.POST.get('h2_custom') or None,
                h3_custom=request.POST.get('h3_custom') or None,
            )
            return HttpResponseRedirect('/admin/products')
        except Exception as e:
            pass
    
    # Render edit form - similar to new form but with product data
    from fasthtml.common import Div, Form, Input, Textarea, Select, Option, Label, Button, A
    categories = ProductRepository.get_categories()
    
    form = Form(method="post", cls="space-y-4")(
        Div(cls="grid grid-cols-1 md:grid-cols-2 gap-4")(
            Div(
                Label("Tên sản phẩm *", cls="block text-sm font-medium text-gray-700 mb-1"),
                Input(type="text", name="name", value=product.get('name', ''), required=True, cls="w-full px-3 py-2 border border-gray-300 rounded"),
            ),
            Div(
                Label("Danh mục *", cls="block text-sm font-medium text-gray-700 mb-1"),
                Select(name="category", required=True, cls="w-full px-3 py-2 border border-gray-300 rounded")(
                    *[Option(value=cat, selected=cat==product.get('category'))(cat) for cat in categories]
                ),
            ),
            Div(
                Label("Giá *", cls="block text-sm font-medium text-gray-700 mb-1"),
                Input(type="number", name="price", value=product.get('price', 0), required=True, cls="w-full px-3 py-2 border border-gray-300 rounded"),
            ),
            Div(
                Label("Giá gốc", cls="block text-sm font-medium text-gray-700 mb-1"),
                Input(type="number", name="original_price", value=product.get('original_price') or '', cls="w-full px-3 py-2 border border-gray-300 rounded"),
            ),
        ),
        Div(
            Label("Mô tả", cls="block text-sm font-medium text-gray-700 mb-1"),
            Textarea(name="description", rows=4, cls="w-full px-3 py-2 border border-gray-300 rounded")(product.get('description') or ''),
        ),
        Div(cls="flex gap-2")(
            Button(type="submit", cls="px-4 py-2 bg-[#2F5233] text-white rounded hover:bg-[#1a331d] transition")("Lưu"),
            A(href="/admin/products", cls="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition")("Hủy"),
        ),
    )
    
    content = Div(cls="space-y-4")(
        Div(cls="text-sm text-gray-600 mb-4")(f"Sửa sản phẩm #{id}"),
        form,
    )
    
    mock_req = MockRequest(request)
    html_obj = AdminViews.layout(mock_req, "Sửa Sản phẩm", content)
    html_str = _render_html(html_obj)
    response = HttpResponse(html_str, content_type='text/html; charset=utf-8')
    return response


@require_http_methods(["POST"])
def admin_product_delete(request, id):
    """Delete product."""
    ProductRepository.delete(id)
    return HttpResponseRedirect('/admin/products')


# Similar implementations for news, categories, pages, hero, site...
# (Keeping existing implementations but ensuring they use MockRequest)

def admin_news(request):
    """Admin news list."""
    search = request.GET.get('search', '')
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1
    
    items, total = NewsRepository.search(search=search, page=page, per_page=10)
    total_pages = max(1, (total + 9) // 10)
    
    from fasthtml.common import Div, Table, Thead, Tbody, Tr, Th, Td, A, Button, Input, Form, Img, Span
    from urllib.parse import urlencode
    
    rows = []
    for item in items:
        item_id = item.get("id")
        if item_id is None:
            continue
        
        # Get image URL
        image_url = item.get("image", "") or ""
        image_cell = Td(cls="px-4 py-3")
        if image_url:
            image_cell = Td(
                Img(
                    src=image_url,
                    alt="",
                    cls="w-16 h-16 object-cover rounded border border-gray-200",
                    style="max-width: 64px; max-height: 64px;"
                ),
                cls="px-4 py-3"
            )
        else:
            image_cell = Td(
                Span("—", cls="text-gray-400"),
                cls="px-4 py-3 text-sm text-gray-400"
            )
        
        # Get author
        author = item.get("author", "") or ""
        author_cell = Td(
            author if author else Span("—", cls="text-gray-400"),
            cls="px-4 py-3 text-sm text-gray-600"
        )
        
        rows.append(
            Tr(cls="hover:bg-gray-50 transition")(
                Td(
                    Input(
                        type="checkbox",
                        name="news_ids",
                        value=str(item_id),
                        cls="news-checkbox rounded border-gray-300 text-[#2F5233] focus:ring-[#2F5233]",
                        id=f"news-{item_id}"
                    ),
                    cls="px-4 py-3"
                ),
                Td(str(item_id), cls="px-4 py-3 text-sm text-gray-700"),
                Td(
                    A(href=f"/admin/news/{item_id}/edit", cls="font-medium text-[#2F5233] hover:underline")(
                        (item.get("title", "") or "")[:50] + ("..." if len(item.get("title", "") or "") > 50 else "")
                    ),
                    cls="px-4 py-3"
                ),
                image_cell,
                author_cell,
                Td(item.get("date", ""), cls="px-4 py-3 text-sm text-gray-600"),
                Td(
                    A(href=f"/admin/news/{item_id}/edit", cls="px-2 py-1 text-xs rounded bg-blue-100 text-blue-700 hover:bg-blue-200 transition")("Sửa"),
                    " ",
                    Button(
                        type="button",
                        onclick=f"confirmDelete({item_id}, '/admin/news/{item_id}/delete')",
                        cls="px-2 py-1 text-xs rounded bg-red-100 text-red-700 hover:bg-red-200 transition"
                    )("Xóa"),
                    cls="px-4 py-3 text-sm space-x-2"
                ),
            )
        )
    
    filters = Form(method="get", cls="mb-4 flex gap-2")(
        Input(
            type="text",
            name="search",
            value=search,
            placeholder="Tìm kiếm...",
            cls="px-3 py-2 border border-gray-300 rounded text-sm flex-1"
        ),
        Button(
            type="submit",
            cls="px-4 py-2 bg-[#2F5233] text-white rounded hover:bg-[#1a331d] transition text-sm"
        )("Lọc"),
        A(
            href="/admin/news/add",
            cls="px-4 py-2 bg-[#E85D04] text-white rounded hover:bg-[#c75003] transition text-sm"
        )("+ Thêm mới"),
    )
    
    pagination = Div()
    if total_pages > 1:
        pag_links = []
        for p in range(1, total_pages + 1):
            params = {"page": str(p)}
            if search:
                params["search"] = search
            url = "/admin/news?" + urlencode(params)
            pag_links.append(
                A(
                    href=url,
                    cls=f"px-3 py-1 rounded text-sm {'bg-[#2F5233] text-white' if p == page else 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'}"
                )(str(p))
            )
        pagination = Div(cls="mt-4 flex items-center justify-between")(
            Div(cls="text-sm text-gray-600")(f"Hiển thị {(page-1)*10 + 1}-{min(page*10, total)} trong {total} tin tức"),
            Div(cls="flex gap-1")(*pag_links),
        )
    
    # Get CSRF token for bulk delete form
    from django.middleware.csrf import get_token
    csrf_token = get_token(request)
    
    # Bulk actions
    bulk_actions = Div(id="bulk-actions", cls="hidden mb-4 p-3 bg-gray-50 rounded border border-gray-200 flex items-center justify-between")(
        Div(cls="flex items-center gap-2")(
            Span(id="selected-count", cls="text-sm font-medium text-gray-700")("0 mục đã chọn"),
        ),
        Div(cls="flex gap-2")(
            Button(
                type="button",
                id="bulk-delete-btn",
                cls="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition text-sm font-medium"
            )("Xóa đã chọn"),
            Button(
                type="button",
                id="bulk-cancel-btn",
                cls="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition text-sm"
            )("Hủy"),
        ),
    )
    
    content = Div(cls="space-y-4")(
        filters,
        bulk_actions,
        Form(id="bulk-delete-form", method="post", action="/admin/news/bulk-delete", cls="hidden")(
            Input(type="hidden", name="csrfmiddlewaretoken", id="bulk-csrf-token", value=csrf_token),
        ),
        Div(cls="bg-white rounded border border-gray-200 overflow-hidden")(
            Table(cls="w-full")(
                Thead(cls="bg-gray-50")(
                    Tr(
                        Th(
                            Input(
                                type="checkbox",
                                id="select-all-news",
                                cls="rounded border-gray-300 text-[#2F5233] focus:ring-[#2F5233]"
                            ),
                            cls="px-4 py-3 w-12"
                        ),
                        Th("ID", cls="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase"),
                        Th("Tiêu đề", cls="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase"),
                        Th("Ảnh", cls="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase"),
                        Th("Tác giả", cls="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase"),
                        Th("Ngày", cls="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase"),
                        Th("Thao tác", cls="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase"),
                    )
                ),
                Tbody(*rows) if rows else Tbody(Tr(Td("Không có tin tức nào", colspan=7, cls="px-4 py-8 text-center text-gray-500"))),
            )
        ),
        pagination,
    )
    
    # Add CSRF token to bulk delete form
    from django.middleware.csrf import get_token
    csrf_token = get_token(request)
    # Inject CSRF token into form via JavaScript
    from fasthtml.common import Script
    csrf_script = Script(f"""
        document.addEventListener('DOMContentLoaded', function() {{
            var csrfInput = document.getElementById('bulk-csrf-token');
            if (csrfInput) {{
                csrfInput.value = '{csrf_token}';
            }}
        }});
    """)
    
    mock_req = MockRequest(request)
    # Pass real request to layout for CSRF token
    html_obj = AdminViews.layout(mock_req, "Quản lý Tin tức", content, django_request=request)
    html_str = _render_html(html_obj)
    response = HttpResponse(html_str, content_type='text/html; charset=utf-8')
    return response


def _build_news_form(news_data=None, request=None):
    """Build professional news editor form with 2-column layout."""
    from fasthtml.common import Div, Form, Input, Textarea, Label, Button, A, H3, I, Span, Img
    from django.middleware.csrf import get_token
    from datetime import datetime
    
    news = news_data or {}
    
    # Get CSRF token
    csrf_token = ''
    if request:
        try:
            csrf_token = get_token(request)
        except Exception:
            # Fallback: try to get from META
            csrf_token = request.META.get('CSRF_COOKIE', '')
    
    image_url = news.get('image', '')
    slug_value = news.get('slug', '')
    title_value = news.get('title', '')
    
    # Auto-set author and date defaults
    author_value = news.get('author', '') or 'Admin'
    date_value = news.get('date', '') or datetime.now().strftime('%Y-%m-%d')
    
    # Generate permalink display
    base_url = "/news/"
    permalink_display = base_url + (slug_value if slug_value else "slug-se-chua-co")
    
    # Left Column - Main Content
    left_column = Div(cls="flex-1 pr-6 space-y-6")(
        # Title Section
        Div(cls="space-y-3")(
            Div(
                Input(
                    type="text",
                    name="title",
                    id="news-title",
                    value=title_value,
                    required=True,
                    cls="w-full text-2xl font-bold border-0 border-b-2 border-gray-300 focus:border-[#2F5233] focus:ring-0 px-0 py-2 bg-transparent",
                    placeholder="Nhập tiêu đề bài viết"
                ),
            ),
            # Permalink
            Div(cls="flex items-center gap-2 text-sm text-gray-600")(
                Span("Permalink:", cls="font-medium"),
                Span(permalink_display, id="permalink-display", cls="text-[#2F5233] font-mono"),
                Button(
                    type="button",
                    id="edit-permalink-btn",
                    cls="px-2 py-1 text-xs text-gray-600 hover:text-[#2F5233] hover:underline",
                    onclick="return false;"
                )("Chỉnh sửa"),
            ),
            Div(id="permalink-edit", cls="hidden")(
                Div(cls="flex items-center gap-2")(
                    Span(base_url, cls="text-sm text-gray-600 font-mono"),
                    Input(
                        type="text",
                        name="slug",
                        id="news-slug",
                        value=slug_value,
                        cls="flex-1 px-2 py-1 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-[#2F5233] focus:border-[#2F5233]",
                        placeholder="url-friendly-slug"
                    ),
                    Button(
                        type="button",
                        id="save-permalink-btn",
                        cls="px-3 py-1 text-xs bg-[#2F5233] text-white rounded hover:bg-[#1a331d]",
                        onclick="return false;"
                    )("OK"),
                ),
            ),
        ),
        
        # Editor Tabs
        Div(cls="border-b border-gray-300 flex gap-1")(
            Button(
                type="button",
                id="editor-tab-visual",
                cls="px-4 py-2 border-b-2 border-[#2F5233] text-[#2F5233] font-medium text-sm cursor-pointer",
                style="pointer-events: auto;"
            )("Visual"),
            Button(
                type="button",
                id="editor-tab-code",
                cls="px-4 py-2 text-gray-600 hover:text-gray-900 font-medium text-sm cursor-pointer",
                style="pointer-events: auto;"
            )("Code"),
        ),
        
        # Content Editor
        Div(cls="space-y-2")(
            Textarea(
                name="content",
                id="news-content",
                cls="hidden"
            )(news.get('content') or ''),
            Div(
                id="news-content-editor",
                cls="bg-white border border-gray-300 rounded",
                style="max-height: 400px; overflow-y: auto;"
            ),
            Div(id="news-content-code", cls="hidden")(
                Textarea(
                    id="news-content-code-textarea",
                    rows=20,
                    cls="w-full px-3 py-2 border border-gray-300 rounded font-mono text-sm",
                    style="max-height: 400px; overflow-y: auto;",
                    placeholder="Nhập HTML code..."
                )(news.get('content') or ''),
            ),
        ),
        
        # Status Bar
        Div(cls="flex items-center justify-between text-xs text-gray-500 pt-2 border-t border-gray-200")(
            Span(id="word-count", cls="")("Word count: 0"),
            Span("Draft saved", cls="text-green-600"),
        ),
    )
    
    # Right Column - Sidebar
    right_column = Div(cls="w-80 space-y-4")(
        # Featured Image Card
        Div(cls="bg-white border border-gray-200 rounded-lg p-4")(
            H3("Featured Image", cls="text-sm font-semibold text-gray-900 mb-3"),
            Div(id="featured-image-container", cls="space-y-3")(
                Div(
                    id="featured-image-placeholder",
                    cls="w-full h-48 bg-gray-100 border-2 border-dashed border-gray-300 rounded flex items-center justify-center"
                )(
                    Span("Chưa có ảnh", cls="text-gray-400 text-sm"),
                ),
                Div(
                    id="featured-image-preview",
                    cls="hidden"
                )(
                    Div(cls="relative")(
                        Img(
                            id="featured-image-preview-img",
                            src="",
                            alt="Featured Image",
                            cls="w-full h-48 object-cover rounded border border-gray-300"
                        ),
                        Button(
                            type="button",
                            id="remove-featured-image",
                            cls="absolute top-2 right-2 px-2 py-1 bg-red-600 text-white rounded text-xs hover:bg-red-700",
                            onclick="return false;"
                        )(
                            I(cls="fas fa-times"),
                        ),
                    ),
                ),
                Div(cls="space-y-2")(
                    Label("URL ảnh", cls="block text-xs font-medium text-gray-700"),
                    Input(
                        type="url",
                        name="image",
                        id="news-cover-image",
                        value=image_url,
                        cls="w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-[#2F5233] focus:border-[#2F5233]",
                        placeholder="Nhập URL ảnh"
                    ),
                ),
            ),
        ),
        
        # Publish Card
        Div(cls="bg-white border border-gray-200 rounded-lg p-4")(
            H3("Publish", cls="text-sm font-semibold text-gray-900 mb-3"),
            Div(cls="space-y-3")(
                Div(
                    Label("Tác giả", cls="block text-xs font-medium text-gray-700 mb-1"),
                    Input(
                        type="text",
                        name="author",
                        value=author_value,
                        readonly=True,
                        cls="w-full px-2 py-1.5 text-sm border border-gray-300 rounded bg-gray-50 text-gray-600 cursor-not-allowed",
                        placeholder="Tác giả"
                    ),
                    Span("Tự động điền", cls="text-xs text-gray-500 mt-1 block"),
                ),
                Div(
                    Label("Ngày đăng", cls="block text-xs font-medium text-gray-700 mb-1"),
                    Div(cls="relative")(
                        Input(
                            type="date",
                            name="date",
                            value=date_value,
                            readonly=True,
                            cls="w-full px-2 py-1.5 text-sm border border-gray-300 rounded bg-gray-50 text-gray-600 cursor-not-allowed"
                        ),
                        I(cls="fas fa-calendar absolute right-2 top-2 text-gray-400 text-xs pointer-events-none"),
                    ),
                    Span("Tự động điền", cls="text-xs text-gray-500 mt-1 block"),
                ),
            ),
        ),
        
        # SEO Card
        Div(cls="bg-white border border-gray-200 rounded-lg p-4")(
            H3("SEO", cls="text-sm font-semibold text-gray-900 mb-3"),
            Div(cls="space-y-3")(
                Div(
                    Label("Meta Title", cls="block text-xs font-medium text-gray-700 mb-1"),
                    Input(
                        type="text",
                        name="meta_title",
                        value=news.get('meta_title', ''),
                        cls="w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-[#2F5233] focus:border-[#2F5233]",
                        placeholder="Meta Title"
                    ),
                ),
                Div(
                    Label("Meta Description", cls="block text-xs font-medium text-gray-700 mb-1"),
                    Div(cls="relative")(
                        Textarea(
                            name="meta_description",
                            id="meta-description",
                            rows=4,
                            cls="w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-[#2F5233] focus:border-[#2F5233] resize-none",
                            placeholder="Meta Description"
                        )(news.get('meta_description') or ''),
                        Span(
                            id="meta-desc-counter",
                            cls="absolute bottom-2 right-2 text-xs text-gray-400"
                        )("0/160"),
                    ),
                ),
                Div(cls="grid grid-cols-3 gap-2")(
                    Div(
                        Label("H1", cls="block text-xs font-medium text-gray-700 mb-1"),
                        Input(
                            type="text",
                            name="h1_custom",
                            value=news.get('h1_custom', ''),
                            cls="w-full px-2 py-1 text-xs border border-gray-300 rounded focus:ring-2 focus:ring-[#2F5233] focus:border-[#2F5233]",
                            placeholder="H1"
                        ),
                    ),
                    Div(
                        Label("H2", cls="block text-xs font-medium text-gray-700 mb-1"),
                        Input(
                            type="text",
                            name="h2_custom",
                            value=news.get('h2_custom', ''),
                            cls="w-full px-2 py-1 text-xs border border-gray-300 rounded focus:ring-2 focus:ring-[#2F5233] focus:border-[#2F5233]",
                            placeholder="H2"
                        ),
                    ),
                    Div(
                        Label("H3", cls="block text-xs font-medium text-gray-700 mb-1"),
                        Input(
                            type="text",
                            name="h3_custom",
                            value=news.get('h3_custom', ''),
                            cls="w-full px-2 py-1 text-xs border border-gray-300 rounded focus:ring-2 focus:ring-[#2F5233] focus:border-[#2F5233]",
                            placeholder="H3"
                        ),
                    ),
                ),
            ),
        ),
    )
    
    # Actions
    actions = Div(cls="flex gap-3 justify-end pt-6 border-t border-gray-200 mt-6")(
        A(
            href="/admin/news",
            cls="px-6 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition font-medium"
        )("Hủy"),
        Button(
            type="submit",
            cls="px-6 py-2 bg-[#2F5233] text-white rounded hover:bg-[#1a331d] transition font-medium"
        )("Lưu"),
    )
    
    # Main Layout - 2 columns
    form = Form(method="post", cls="space-y-0")(
        Input(type="hidden", name="csrfmiddlewaretoken", value=csrf_token),
        Div(cls="flex gap-6 items-start")(
            left_column,
            right_column,
        ),
        actions,
    )
    
    return form


def admin_news_add(request):
    """Add news."""
    if request.method == 'POST':
        try:
            from datetime import datetime
            # Auto-set author and date
            author = request.POST.get('author') or 'Admin'
            date = request.POST.get('date') or datetime.now().strftime('%Y-%m-%d')
            
            NewsRepository.create(
                title=request.POST.get('title', ''),
                slug=request.POST.get('slug') or None,
                image=request.POST.get('image') or None,
                content=request.POST.get('content') or None,
                author=author,
                date=date,
                meta_title=request.POST.get('meta_title') or None,
                meta_description=request.POST.get('meta_description') or None,
                h1_custom=request.POST.get('h1_custom') or None,
                h2_custom=request.POST.get('h2_custom') or None,
                h3_custom=request.POST.get('h3_custom') or None,
            )
            return HttpResponseRedirect('/admin/news')
        except Exception as e:
            pass
    
    from fasthtml.common import Div
    form = _build_news_form(request=request)
    
    content = Div(cls="space-y-4")(
        Div(cls="text-sm text-gray-600 mb-4")("Thêm tin tức mới"),
        form,
    )
    
    mock_req = MockRequest(request)
    html_obj = AdminViews.layout(mock_req, "Thêm Tin tức", content, include_editor=True, django_request=request)
    html_str = _render_html(html_obj)
    response = HttpResponse(html_str, content_type='text/html; charset=utf-8')
    return response


def admin_news_edit(request, id):
    """Edit news."""
    news = NewsRepository.get_by_id_for_edit(id)
    if not news:
        return HttpResponseRedirect('/admin/news')
    
    if request.method == 'POST':
        try:
            from datetime import datetime
            # Auto-set author and date if not provided
            author = request.POST.get('author') or news.get('author') or 'Admin'
            date = request.POST.get('date') or news.get('date') or datetime.now().strftime('%Y-%m-%d')
            
            NewsRepository.update(
                id=id,
                title=request.POST.get('title', ''),
                slug=request.POST.get('slug') or None,
                date=date,
                image=request.POST.get('image') or None,
                content=request.POST.get('content') or None,
                author=author,
                meta_title=request.POST.get('meta_title') or None,
                meta_description=request.POST.get('meta_description') or None,
                h1_custom=request.POST.get('h1_custom') or None,
                h2_custom=request.POST.get('h2_custom') or None,
                h3_custom=request.POST.get('h3_custom') or None,
            )
            return HttpResponseRedirect('/admin/news')
        except Exception as e:
            pass
    
    from fasthtml.common import Div
    form = _build_news_form(news, request=request)
    
    content = Div(cls="space-y-4")(
        Div(cls="text-sm text-gray-600 mb-4")(f"Sửa tin tức #{id}"),
        form,
    )
    
    mock_req = MockRequest(request)
    html_obj = AdminViews.layout(mock_req, "Sửa Tin tức", content, include_editor=True, django_request=request)
    html_str = _render_html(html_obj)
    response = HttpResponse(html_str, content_type='text/html; charset=utf-8')
    return response


@require_http_methods(["POST"])
def admin_news_delete(request, id):
    """Delete news."""
    NewsRepository.delete(id)
    return HttpResponseRedirect('/admin/news')


@require_http_methods(["POST"])
def admin_news_bulk_delete(request):
    """Bulk delete news."""
    from django.middleware.csrf import get_token
    
    news_ids = request.POST.getlist('news_ids')
    if news_ids:
        try:
            # Convert to integers and delete
            ids = [int(nid) for nid in news_ids if nid.isdigit()]
            NewsRepository.bulk_delete(ids)
        except Exception as e:
            pass
    
    return HttpResponseRedirect('/admin/news')


def admin_categories(request):
    """Admin categories list."""
    categories = CategoryRepository.get_all_rows()
    
    from fasthtml.common import Div, Table, Thead, Tbody, Tr, Th, Td, A, Button
    rows = []
    for cat in categories:
        cat_id = cat.get("id")
        if cat_id is None:
            continue
        rows.append(
            Tr(cls="hover:bg-gray-50 transition")(
                Td(str(cat_id), cls="px-4 py-3 text-sm text-gray-700"),
                Td(cat.get("name", ""), cls="px-4 py-3 text-sm font-medium text-gray-900"),
                Td(
                    A(href=f"/admin/categories/{cat_id}/edit", cls="px-2 py-1 text-xs rounded bg-blue-100 text-blue-700 hover:bg-blue-200 transition")("Sửa"),
                    " ",
                    Button(
                        type="button",
                        onclick=f"confirmDelete({cat_id}, '/admin/categories/{cat_id}/delete')",
                        cls="px-2 py-1 text-xs rounded bg-red-100 text-red-700 hover:bg-red-200 transition"
                    )("Xóa"),
                    cls="px-4 py-3 text-sm space-x-2"
                ),
            )
        )
    
    content = Div(cls="space-y-4")(
        A(
            href="/admin/categories/add",
            cls="inline-block px-4 py-2 bg-[#E85D04] text-white rounded hover:bg-[#c75003] transition text-sm mb-4"
        )("+ Thêm danh mục"),
        Div(cls="bg-white rounded border border-gray-200 overflow-hidden")(
            Table(cls="w-full")(
                Thead(cls="bg-gray-50")(
                    Tr(
                        Th("ID", cls="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase"),
                        Th("Tên", cls="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase"),
                        Th("Thao tác", cls="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase"),
                    )
                ),
                Tbody(*rows) if rows else Tbody(Tr(Td("Không có danh mục nào", colspan=3, cls="px-4 py-8 text-center text-gray-500"))),
            )
        ),
    )
    
    mock_req = MockRequest(request)
    html_obj = AdminViews.layout(mock_req, "Quản lý Danh mục", content)
    html_str = _render_html(html_obj)
    response = HttpResponse(html_str, content_type='text/html; charset=utf-8')
    return response


def admin_category_add(request):
    """Add category."""
    if request.method == 'POST':
        try:
            CategoryRepository.create(
                name=request.POST.get('name', ''),
                sort_order=int(request.POST.get('sort_order', 0)),
            )
            return HttpResponseRedirect('/admin/categories')
        except Exception as e:
            pass
    
    from fasthtml.common import Div, Form, Input, Label, Button, A
    form = Form(method="post", cls="space-y-4")(
        Div(
            Label("Tên danh mục *", cls="block text-sm font-medium text-gray-700 mb-1"),
            Input(type="text", name="name", required=True, cls="w-full px-3 py-2 border border-gray-300 rounded"),
        ),
        Div(cls="flex gap-2")(
            Button(type="submit", cls="px-4 py-2 bg-[#2F5233] text-white rounded hover:bg-[#1a331d] transition")("Lưu"),
            A(href="/admin/categories", cls="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition")("Hủy"),
        ),
    )
    
    content = Div(cls="space-y-4")(
        Div(cls="text-sm text-gray-600 mb-4")("Thêm danh mục mới"),
        form,
    )
    
    mock_req = MockRequest(request)
    html_obj = AdminViews.layout(mock_req, "Thêm Danh mục", content)
    html_str = _render_html(html_obj)
    response = HttpResponse(html_str, content_type='text/html; charset=utf-8')
    return response


def admin_category_edit(request, id):
    """Edit category."""
    category = CategoryRepository.get_by_id(id)
    if not category:
        return HttpResponseRedirect('/admin/categories')
    
    if request.method == 'POST':
        try:
            CategoryRepository.update(
                id=id,
                name=request.POST.get('name', ''),
                sort_order=int(request.POST.get('sort_order', 0)),
            )
            return HttpResponseRedirect('/admin/categories')
        except Exception as e:
            pass
    
    from fasthtml.common import Div, Form, Input, Label, Button, A
    form = Form(method="post", cls="space-y-4")(
        Div(
            Label("Tên danh mục *", cls="block text-sm font-medium text-gray-700 mb-1"),
            Input(type="text", name="name", value=category.get('name', ''), required=True, cls="w-full px-3 py-2 border border-gray-300 rounded"),
        ),
        Div(cls="flex gap-2")(
            Button(type="submit", cls="px-4 py-2 bg-[#2F5233] text-white rounded hover:bg-[#1a331d] transition")("Lưu"),
            A(href="/admin/categories", cls="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition")("Hủy"),
        ),
    )
    
    content = Div(cls="space-y-4")(
        Div(cls="text-sm text-gray-600 mb-4")(f"Sửa danh mục #{id}"),
        form,
    )
    
    mock_req = MockRequest(request)
    html_obj = AdminViews.layout(mock_req, "Sửa Danh mục", content)
    html_str = _render_html(html_obj)
    response = HttpResponse(html_str, content_type='text/html; charset=utf-8')
    return response


@require_http_methods(["POST"])
def admin_category_delete(request, id):
    """Delete category."""
    CategoryRepository.delete(id)
    return HttpResponseRedirect('/admin/categories')


def admin_pages(request):
    """Admin pages list."""
    pages = PageRepository.get_all()
    
    from fasthtml.common import Div, Table, Thead, Tbody, Tr, Th, Td, A, Button
    rows = []
    for page in pages:
        page_id = page.get("id")
        if page_id is None:
            continue
        rows.append(
            Tr(cls="hover:bg-gray-50 transition")(
                Td(str(page_id), cls="px-4 py-3 text-sm text-gray-700"),
                Td(page.get("slug", ""), cls="px-4 py-3 text-sm font-medium text-gray-900"),
                Td(page.get("title", ""), cls="px-4 py-3 text-sm text-gray-600"),
                Td(
                    A(href=f"/admin/pages/{page_id}/edit", cls="px-2 py-1 text-xs rounded bg-blue-100 text-blue-700 hover:bg-blue-200 transition")("Sửa"),
                    " ",
                    Button(
                        type="button",
                        onclick=f"confirmDelete({page_id}, '/admin/pages/{page_id}/delete')",
                        cls="px-2 py-1 text-xs rounded bg-red-100 text-red-700 hover:bg-red-200 transition"
                    )("Xóa"),
                    cls="px-4 py-3 text-sm space-x-2"
                ),
            )
        )
    
    content = Div(cls="space-y-4")(
        A(
            href="/admin/pages/add",
            cls="inline-block px-4 py-2 bg-[#E85D04] text-white rounded hover:bg-[#c75003] transition text-sm mb-4"
        )("+ Thêm trang"),
        Div(cls="bg-white rounded border border-gray-200 overflow-hidden")(
            Table(cls="w-full")(
                Thead(cls="bg-gray-50")(
                    Tr(
                        Th("ID", cls="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase"),
                        Th("Slug", cls="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase"),
                        Th("Tiêu đề", cls="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase"),
                        Th("Thao tác", cls="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase"),
                    )
                ),
                Tbody(*rows) if rows else Tbody(Tr(Td("Không có trang nào", colspan=4, cls="px-4 py-8 text-center text-gray-500"))),
            )
        ),
    )
    
    mock_req = MockRequest(request)
    html_obj = AdminViews.layout(mock_req, "Quản lý Trang", content)
    html_str = _render_html(html_obj)
    response = HttpResponse(html_str, content_type='text/html; charset=utf-8')
    return response


def admin_page_add(request):
    """Add page."""
    if request.method == 'POST':
        try:
            PageRepository.create(
                slug=request.POST.get('slug', ''),
                title=request.POST.get('title', ''),
                content=request.POST.get('content') or None,
                meta_title=request.POST.get('meta_title') or None,
                meta_description=request.POST.get('meta_description') or None,
                sort_order=int(request.POST.get('sort_order', 0)),
            )
            return HttpResponseRedirect('/admin/pages')
        except Exception as e:
            pass
    
    from fasthtml.common import Div, Form, Input, Textarea, Label, Button, A
    form = Form(method="post", cls="space-y-4")(
        Div(
            Label("Slug *", cls="block text-sm font-medium text-gray-700 mb-1"),
            Input(type="text", name="slug", required=True, cls="w-full px-3 py-2 border border-gray-300 rounded"),
        ),
        Div(
            Label("Tiêu đề *", cls="block text-sm font-medium text-gray-700 mb-1"),
            Input(type="text", name="title", required=True, cls="w-full px-3 py-2 border border-gray-300 rounded"),
        ),
        Div(
            Label("Nội dung", cls="block text-sm font-medium text-gray-700 mb-1"),
            Textarea(name="content", rows=10, cls="w-full px-3 py-2 border border-gray-300 rounded"),
        ),
        Div(cls="flex gap-2")(
            Button(type="submit", cls="px-4 py-2 bg-[#2F5233] text-white rounded hover:bg-[#1a331d] transition")("Lưu"),
            A(href="/admin/pages", cls="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition")("Hủy"),
        ),
    )
    
    content = Div(cls="space-y-4")(
        Div(cls="text-sm text-gray-600 mb-4")("Thêm trang mới"),
        form,
    )
    
    mock_req = MockRequest(request)
    html_obj = AdminViews.layout(mock_req, "Thêm Trang", content)
    html_str = _render_html(html_obj)
    response = HttpResponse(html_str, content_type='text/html; charset=utf-8')
    return response


def admin_page_edit(request, id):
    """Edit page."""
    page = PageRepository.get_by_id(id)
    if not page:
        return HttpResponseRedirect('/admin/pages')
    
    if request.method == 'POST':
        try:
            PageRepository.update(
                id=id,
                slug=request.POST.get('slug', ''),
                title=request.POST.get('title', ''),
                content=request.POST.get('content') or None,
                meta_title=request.POST.get('meta_title') or None,
                meta_description=request.POST.get('meta_description') or None,
                sort_order=int(request.POST.get('sort_order', 0)),
            )
            return HttpResponseRedirect('/admin/pages')
        except Exception as e:
            pass
    
    from fasthtml.common import Div, Form, Input, Textarea, Label, Button, A
    form = Form(method="post", cls="space-y-4")(
        Div(
            Label("Slug *", cls="block text-sm font-medium text-gray-700 mb-1"),
            Input(type="text", name="slug", value=page.get('slug', ''), required=True, cls="w-full px-3 py-2 border border-gray-300 rounded"),
        ),
        Div(
            Label("Tiêu đề *", cls="block text-sm font-medium text-gray-700 mb-1"),
            Input(type="text", name="title", value=page.get('title', ''), required=True, cls="w-full px-3 py-2 border border-gray-300 rounded"),
        ),
        Div(
            Label("Nội dung", cls="block text-sm font-medium text-gray-700 mb-1"),
            Textarea(name="content", rows=10, cls="w-full px-3 py-2 border border-gray-300 rounded")(page.get('content') or ''),
        ),
        Div(cls="flex gap-2")(
            Button(type="submit", cls="px-4 py-2 bg-[#2F5233] text-white rounded hover:bg-[#1a331d] transition")("Lưu"),
            A(href="/admin/pages", cls="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition")("Hủy"),
        ),
    )
    
    content = Div(cls="space-y-4")(
        Div(cls="text-sm text-gray-600 mb-4")(f"Sửa trang #{id}"),
        form,
    )
    
    mock_req = MockRequest(request)
    html_obj = AdminViews.layout(mock_req, "Sửa Trang", content)
    html_str = _render_html(html_obj)
    response = HttpResponse(html_str, content_type='text/html; charset=utf-8')
    return response


@require_http_methods(["POST"])
def admin_page_delete(request, id):
    """Delete page."""
    PageRepository.delete(id)
    return HttpResponseRedirect('/admin/pages')


def admin_hero(request):
    """Admin hero."""
    hero = HeroRepository.get_for_edit()
    
    from fasthtml.common import Div, Form, Input, Label, Button, Textarea, Span, Img, Script
    from django.middleware.csrf import get_token
    
    # Get CSRF token
    csrf_token = ''
    try:
        csrf_token = get_token(request)
    except Exception:
        csrf_token = request.META.get('CSRF_COOKIE', '')
    
    # Configuration Form (Left Column)
    config_form = Form(method="post", action="/admin/hero/save", cls="space-y-4", id="hero-form")(
        Input(type="hidden", name="csrfmiddlewaretoken", value=csrf_token),
        Div(cls="space-y-4")(
            Div(
                Label("Promo (nhãn nhỏ)", cls="block text-sm font-medium text-gray-700 mb-1"),
                Input(
                    type="text",
                    name="promo",
                    id="hero-promo",
                    value=hero.get('promo', ''),
                    cls="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-[#2F5233] focus:border-[#2F5233]",
                    oninput="updatePreview()"
                ),
            ),
            Div(
                Label("Tiêu đề chính", cls="block text-sm font-medium text-gray-700 mb-1"),
                Input(
                    type="text",
                    name="title",
                    id="hero-title",
                    value=hero.get('title', ''),
                    cls="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-[#2F5233] focus:border-[#2F5233]",
                    oninput="updatePreview()"
                ),
            ),
            Div(
                Label("Phụ đề", cls="block text-sm font-medium text-gray-700 mb-1"),
                Textarea(
                    name="subtitle",
                    id="hero-subtitle",
                    rows=3,
                    cls="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-[#2F5233] focus:border-[#2F5233] resize-none",
                    oninput="updatePreview()"
                )(hero.get('subtitle', '')),
            ),
            Div(
                Label("URL ảnh", cls="block text-sm font-medium text-gray-700 mb-1"),
                Input(
                    type="url",
                    name="image",
                    id="hero-image",
                    value=hero.get('image', ''),
                    cls="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-[#2F5233] focus:border-[#2F5233]",
                    oninput="updatePreview()"
                ),
                Span("Nhập URL ảnh từ Unsplash, Cloudinary hoặc CDN khác", cls="text-xs text-gray-500 mt-1 block"),
            ),
            Div(
                Label("Nút CTA", cls="block text-sm font-medium text-gray-700 mb-1"),
                Input(
                    type="text",
                    name="button_text",
                    id="hero-button",
                    value=hero.get('button_text', ''),
                    cls="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-[#2F5233] focus:border-[#2F5233]",
                    oninput="updatePreview()"
                ),
            ),
            Button(type="submit", cls="px-6 py-2 bg-[#2F5233] text-white rounded hover:bg-[#1a331d] transition font-medium w-full")("Lưu thay đổi"),
        ),
    )
    
    # Preview Section (Right Column)
    preview_section = Div(cls="bg-gray-100 rounded-lg border border-gray-200 p-6 sticky top-4")(
        Div(cls="mb-4")(
            Span("Preview", cls="text-lg font-bold text-gray-900 block mb-1"),
            Span("Xem trước hero banner", cls="text-sm text-gray-600"),
        ),
        Div(
            id="hero-preview",
            cls="relative w-full h-96 rounded-lg overflow-hidden shadow-lg",
            style="min-height: 400px;"
        )(
            Div(
                id="hero-preview-bg",
                cls="absolute inset-0 bg-cover bg-center bg-no-repeat",
                style=f"background-image: url('{hero.get('image', '') or 'https://via.placeholder.com/1200x600/2F5233/ffffff?text=Hero+Banner'}');"
            ),
            Div(cls="absolute inset-0 bg-black/40"),
            Div(cls="absolute inset-0 flex flex-col items-center justify-center p-8 text-center")(
                Div(
                    id="hero-preview-promo",
                    cls="inline-block px-4 py-1.5 rounded-full bg-[#E85D04] text-white text-sm font-semibold mb-4 uppercase tracking-wide"
                )(hero.get('promo', 'SUMMER SALE') or 'SUMMER SALE'),
                Div(
                    id="hero-preview-title",
                    cls="text-4xl md:text-5xl font-bold text-white mb-4 leading-tight"
                )(hero.get('title', 'Fresh Produce For Green Living') or 'Fresh Produce For Green Living'),
                Div(
                    id="hero-preview-subtitle",
                    cls="text-lg md:text-xl text-white/90 mb-6 max-w-2xl"
                )(hero.get('subtitle', 'Up to 20% off on vegetables and fruits this week.') or 'Up to 20% off on vegetables and fruits this week.'),
                Button(
                    id="hero-preview-button",
                    type="button",
                    cls="px-8 py-3 bg-[#2F5233] text-white rounded-lg font-semibold text-lg hover:bg-[#1a331d] transition shadow-lg"
                )(hero.get('button_text', 'Shop Now') or 'Shop Now'),
            ),
        ),
    )
    
    # Main Content Layout
    config_section = Div(cls="flex-1 pr-6")(
        Div(cls="mb-4")(
            Span("Cấu hình Hero", cls="text-lg font-bold text-gray-900 block mb-1"),
            Span("Thiết lập banner hero hiển thị ở trang chủ", cls="text-sm text-gray-600"),
        ),
        config_form,
    )
    
    content = Div(cls="space-y-6")(
        Div(cls="mb-6")(
            Span("Hero Banner", cls="text-xl font-bold text-gray-900 block mb-1"),
            Span("Quản lý banner hero hiển thị ở trang chủ", cls="text-sm text-gray-600"),
        ),
        Div(cls="grid grid-cols-1 lg:grid-cols-2 gap-6")(
            config_section,
            preview_section,
        ),
    )
    
    # Add preview script
    preview_script = Script("""
        function updatePreview() {
            const promoEl = document.getElementById('hero-promo');
            const titleEl = document.getElementById('hero-title');
            const subtitleEl = document.getElementById('hero-subtitle');
            const imageEl = document.getElementById('hero-image');
            const buttonEl = document.getElementById('hero-button');
            
            if (!promoEl || !titleEl || !subtitleEl || !imageEl || !buttonEl) return;
            
            const promo = promoEl.value || 'SUMMER SALE';
            const title = titleEl.value || 'Fresh Produce For Green Living';
            const subtitle = subtitleEl.value || 'Up to 20% off on vegetables and fruits this week.';
            const image = imageEl.value || 'https://via.placeholder.com/1200x600/2F5233/ffffff?text=Hero+Banner';
            const button = buttonEl.value || 'Shop Now';
            
            const promoPreview = document.getElementById('hero-preview-promo');
            const titlePreview = document.getElementById('hero-preview-title');
            const subtitlePreview = document.getElementById('hero-preview-subtitle');
            const buttonPreview = document.getElementById('hero-preview-button');
            const bgDiv = document.getElementById('hero-preview-bg');
            
            if (promoPreview) promoPreview.textContent = promo.toUpperCase();
            if (titlePreview) titlePreview.textContent = title;
            if (subtitlePreview) subtitlePreview.textContent = subtitle;
            if (buttonPreview) buttonPreview.textContent = button;
            if (bgDiv) bgDiv.style.backgroundImage = `url('${image}')`;
        }
        
        // Initialize preview on load
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', updatePreview);
        } else {
            updatePreview();
        }
    """)
    
    mock_req = MockRequest(request)
    html_obj = AdminViews.layout(mock_req, "Hero", content)
    
    # Add script to the HTML
    html_str = _render_html(html_obj)
    # Insert script before closing body tag
    if '</body>' in html_str:
        html_str = html_str.replace('</body>', str(preview_script) + '</body>')
    else:
        html_str = html_str + str(preview_script)
    
    response = HttpResponse(html_str, content_type='text/html; charset=utf-8')
    return response


@require_http_methods(["POST"])
def admin_hero_save(request):
    """Save hero."""
    HeroRepository.update(
        promo=request.POST.get('promo') or None,
        title=request.POST.get('title') or None,
        subtitle=request.POST.get('subtitle') or None,
        image=request.POST.get('image') or None,
        button_text=request.POST.get('button_text') or None,
    )
    return HttpResponseRedirect('/admin/hero')


def admin_site(request):
    """Admin site config."""
    config = SiteConfigRepository.get_all()
    brochures = CategoryRepository.get_brochures_for_admin()
    
    from fasthtml.common import Div, Form, Input, Label, Button, H3, Span, A, Table, Thead, Tbody, Tr, Th, Td, Textarea
    from django.middleware.csrf import get_token
    
    # Get CSRF token
    csrf_token = ''
    try:
        csrf_token = get_token(request)
    except Exception:
        csrf_token = request.META.get('CSRF_COOKIE', '')
    
    # Parse configs - handle both dict and JSON string
    import json
    brand = config.get('brand', {})
    if isinstance(brand, str):
        try:
            brand = json.loads(brand)
        except:
            brand = {}
    
    topbar = config.get('topbar', {})
    if isinstance(topbar, str):
        try:
            topbar = json.loads(topbar)
        except:
            topbar = {}
    
    footer = config.get('footer', {})
    if isinstance(footer, str):
        try:
            footer = json.loads(footer)
        except:
            footer = {}
    
    # Get active tab from query param
    active_tab = request.GET.get('tab', 'brand')
    
    # Brand Tab Content
    brand_form = Form(method="post", action="/admin/site/brand", cls="space-y-4")(
        Input(type="hidden", name="csrfmiddlewaretoken", value=csrf_token),
        Div(cls="space-y-4")(
            Div(
                Label("Tên ứng dụng", cls="block text-sm font-medium text-gray-700 mb-1"),
                Input(type="text", name="site_name", value=brand.get('siteName', ''), cls="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-[#2F5233] focus:border-[#2F5233]"),
            ),
            Div(
                Label("Tagline / Slogan", cls="block text-sm font-medium text-gray-700 mb-1"),
                Input(type="text", name="tagline", value=brand.get('tagline', ''), cls="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-[#2F5233] focus:border-[#2F5233]"),
            ),
            Div(
                Label("Icon (Font Awesome)", cls="block text-sm font-medium text-gray-700 mb-1"),
                Input(type="text", name="icon", value=brand.get('icon', ''), cls="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-[#2F5233] focus:border-[#2F5233]"),
                Span("Ví dụ: fas fa-mountain, fas fa-leaf, fas fa-apple-alt", cls="text-xs text-gray-500 mt-1 block"),
            ),
            Button(type="submit", cls="px-6 py-2 bg-[#2F5233] text-white rounded hover:bg-[#1a331d] transition font-medium")("Lưu thay đổi"),
        ),
    )
    
    # Topbar Tab Content
    topbar_form = Form(method="post", action="/admin/site/topbar", cls="space-y-4")(
        Input(type="hidden", name="csrfmiddlewaretoken", value=csrf_token),
        Div(cls="space-y-4")(
            Div(
                Label("Miễn phí vận chuyển", cls="block text-sm font-medium text-gray-700 mb-1"),
                Input(type="text", name="free_shipping", value=topbar.get('freeShipping', ''), cls="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-[#2F5233] focus:border-[#2F5233]"),
            ),
            Div(
                Label("Hotline", cls="block text-sm font-medium text-gray-700 mb-1"),
                Input(type="text", name="hotline", value=topbar.get('hotline', ''), cls="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-[#2F5233] focus:border-[#2F5233]"),
            ),
            Div(
                Label("Hỗ trợ", cls="block text-sm font-medium text-gray-700 mb-1"),
                Input(type="text", name="support", value=topbar.get('support', ''), cls="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-[#2F5233] focus:border-[#2F5233]"),
            ),
            Button(type="submit", cls="px-6 py-2 bg-[#2F5233] text-white rounded hover:bg-[#1a331d] transition font-medium")("Lưu thay đổi"),
        ),
    )
    
    # Footer Tab Content
    footer_form = Form(method="post", action="/admin/site/footer", cls="space-y-4")(
        Input(type="hidden", name="csrfmiddlewaretoken", value=csrf_token),
        Div(cls="space-y-4")(
            Div(
                Label("Địa chỉ", cls="block text-sm font-medium text-gray-700 mb-1"),
                Input(type="text", name="address", value=footer.get('address', ''), cls="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-[#2F5233] focus:border-[#2F5233]"),
            ),
            Div(
                Label("Điện thoại", cls="block text-sm font-medium text-gray-700 mb-1"),
                Input(type="text", name="phone", value=footer.get('phone', ''), cls="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-[#2F5233] focus:border-[#2F5233]"),
            ),
            Div(
                Label("Email", cls="block text-sm font-medium text-gray-700 mb-1"),
                Input(type="email", name="email", value=footer.get('email', ''), cls="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-[#2F5233] focus:border-[#2F5233]"),
            ),
            Div(
                Label("Mô tả", cls="block text-sm font-medium text-gray-700 mb-1"),
                Textarea(name="description", rows=3, cls="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-[#2F5233] focus:border-[#2F5233]")(footer.get('description', '')),
            ),
            Div(
                Label("Copyright", cls="block text-sm font-medium text-gray-700 mb-1"),
                Input(type="text", name="copyright", value=footer.get('copyright', ''), cls="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-[#2F5233] focus:border-[#2F5233]"),
            ),
            Button(type="submit", cls="px-6 py-2 bg-[#2F5233] text-white rounded hover:bg-[#1a331d] transition font-medium")("Lưu thay đổi"),
        ),
    )
    
    # Brochures Tab Content
    brochure_rows = []
    for brochure in brochures:
        brochure_rows.append(
            Tr(cls="hover:bg-gray-50 transition")(
                Td(brochure.get('slug', ''), cls="px-4 py-3 text-sm font-medium text-gray-900"),
                Td(brochure.get('title', '') or '—', cls="px-4 py-3 text-sm text-gray-600"),
                Td(
                    A(href=f"/admin/site/brochure/{brochure.get('slug', '')}/edit", cls="px-2 py-1 text-xs rounded bg-blue-100 text-blue-700 hover:bg-blue-200 transition")("Sửa"),
                    cls="px-4 py-3 text-sm"
                ),
            )
        )
    
    brochures_content = Div(cls="space-y-4")(
        Div(cls="bg-white rounded border border-gray-200 overflow-hidden")(
            Table(cls="w-full")(
                Thead(cls="bg-gray-50")(
                    Tr(
                        Th("Slug", cls="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase"),
                        Th("Tiêu đề", cls="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase"),
                        Th("Thao tác", cls="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase"),
                    )
                ),
                Tbody(*brochure_rows) if brochure_rows else Tbody(Tr(Td("Không có brochure nào", colspan=3, cls="px-4 py-8 text-center text-gray-500"))),
            )
        ),
    )
    
    # Tab Navigation
    tabs = [
        ("brand", "Thương hiệu", active_tab == "brand"),
        ("topbar", "Topbar", active_tab == "topbar"),
        ("footer", "Footer", active_tab == "footer"),
        ("brochures", "Brochures", active_tab == "brochures"),
    ]
    
    tab_buttons = Div(cls="flex gap-1 border-b border-gray-200 mb-6")(
        *[
            A(
                href=f"/admin/site?tab={tab_id}",
                cls=f"px-4 py-2 text-sm font-medium transition-colors {'bg-[#2F5233] text-white' if is_active else 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'}",
            )(label)
            for tab_id, label, is_active in tabs
        ]
    )
    
    # Tab Content
    tab_content = Div()
    if active_tab == "brand":
        tab_content = Div(cls="space-y-4")(
            Div(cls="mb-4")(
                H3("Thương hiệu", cls="text-lg font-bold text-gray-900 mb-1"),
                Span("Cấu hình tên app, tagline và icon hiển thị ở header và footer", cls="text-sm text-gray-600"),
            ),
            brand_form,
        )
    elif active_tab == "topbar":
        tab_content = Div(cls="space-y-4")(
            Div(cls="mb-4")(
                H3("Topbar", cls="text-lg font-bold text-gray-900 mb-1"),
                Span("Cấu hình thông tin hiển thị ở topbar", cls="text-sm text-gray-600"),
            ),
            topbar_form,
        )
    elif active_tab == "footer":
        tab_content = Div(cls="space-y-4")(
            Div(cls="mb-4")(
                H3("Footer", cls="text-lg font-bold text-gray-900 mb-1"),
                Span("Cấu hình thông tin hiển thị ở footer", cls="text-sm text-gray-600"),
            ),
            footer_form,
        )
    elif active_tab == "brochures":
        tab_content = Div(cls="space-y-4")(
            Div(cls="mb-4")(
                H3("Brochures", cls="text-lg font-bold text-gray-900 mb-1"),
                Span("Quản lý brochures hiển thị trên trang chủ", cls="text-sm text-gray-600"),
            ),
            brochures_content,
        )
    
    # Main Content Section
    content = Div(cls="bg-white rounded-lg border border-gray-200 p-6")(
        Div(cls="mb-6")(
            H3("Cấu hình site", cls="text-xl font-bold text-gray-900 mb-1"),
            Span("Quản lý cấu hình thương hiệu, topbar, footer và brochures", cls="text-sm text-gray-600"),
        ),
        tab_buttons,
        tab_content,
    )
    
    mock_req = MockRequest(request)
    html_obj = AdminViews.layout(mock_req, "Site Config", content)
    html_str = _render_html(html_obj)
    response = HttpResponse(html_str, content_type='text/html; charset=utf-8')
    return response


@require_http_methods(["POST"])
def admin_site_brand(request):
    """Update brand config."""
    SiteConfigRepository.update_brand(
        site_name=request.POST.get('site_name', ''),
        tagline=request.POST.get('tagline', ''),
        icon=request.POST.get('icon', ''),
    )
    return HttpResponseRedirect('/admin/site')


@require_http_methods(["POST"])
def admin_site_topbar(request):
    """Update topbar config."""
    SiteConfigRepository.update_topbar(
        free_shipping=request.POST.get('free_shipping', ''),
        hotline=request.POST.get('hotline', ''),
        support=request.POST.get('support') or None,
    )
    return HttpResponseRedirect('/admin/site')


@require_http_methods(["POST"])
def admin_site_footer(request):
    """Update footer config."""
    SiteConfigRepository.update_footer(
        address=request.POST.get('address', ''),
        phone=request.POST.get('phone', ''),
        email=request.POST.get('email', ''),
        description=request.POST.get('description') or None,
        copyright=request.POST.get('copyright') or None,
    )
    return HttpResponseRedirect('/admin/site')


def admin_site_brochure_edit(request, slug):
    """Edit brochure."""
    from api.models.category_brochure import CategoryBrochure
    from django.middleware.csrf import get_token
    from fasthtml.common import Div, Form, Input, Label, Button, A, Textarea
    
    try:
        brochure = CategoryBrochure.objects.get(slug=slug)
    except CategoryBrochure.DoesNotExist:
        return HttpResponseRedirect('/admin/site?tab=brochures')
    
    if request.method == 'POST':
        CategoryRepository.update_brochure(
            slug=slug,
            title=request.POST.get('title') or None,
            desc=request.POST.get('desc') or None,
            image=request.POST.get('image') or None,
            button_text=request.POST.get('button_text') or None,
        )
        return HttpResponseRedirect('/admin/site?tab=brochures')
    
    # Get CSRF token
    csrf_token = ''
    try:
        csrf_token = get_token(request)
    except Exception:
        csrf_token = request.META.get('CSRF_COOKIE', '')
    
    form = Form(method="post", cls="space-y-4")(
        Input(type="hidden", name="csrfmiddlewaretoken", value=csrf_token),
        Div(cls="space-y-4")(
            Div(
                Label("Slug", cls="block text-sm font-medium text-gray-700 mb-1"),
                Input(type="text", value=brochure.slug, readonly=True, cls="w-full px-3 py-2 border border-gray-300 rounded bg-gray-50 text-gray-600 cursor-not-allowed"),
            ),
            Div(
                Label("Tiêu đề", cls="block text-sm font-medium text-gray-700 mb-1"),
                Input(type="text", name="title", value=brochure.title or '', cls="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-[#2F5233] focus:border-[#2F5233]"),
            ),
            Div(
                Label("Mô tả", cls="block text-sm font-medium text-gray-700 mb-1"),
                Textarea(name="desc", rows=4, cls="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-[#2F5233] focus:border-[#2F5233]")(brochure.desc or ''),
            ),
            Div(
                Label("Hình ảnh (URL)", cls="block text-sm font-medium text-gray-700 mb-1"),
                Input(type="url", name="image", value=brochure.image or '', cls="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-[#2F5233] focus:border-[#2F5233]"),
            ),
            Div(
                Label("Nút", cls="block text-sm font-medium text-gray-700 mb-1"),
                Input(type="text", name="button_text", value=brochure.button_text or '', cls="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-[#2F5233] focus:border-[#2F5233]"),
            ),
            Div(cls="flex gap-2")(
                Button(type="submit", cls="px-6 py-2 bg-[#2F5233] text-white rounded hover:bg-[#1a331d] transition font-medium")("Lưu thay đổi"),
                A(href="/admin/site?tab=brochures", cls="px-6 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition font-medium")("Hủy"),
            ),
        ),
    )
    
    content = Div(cls="bg-white rounded-lg border border-gray-200 p-6")(
        Div(cls="mb-6")(
            Div(cls="text-xl font-bold text-gray-900 mb-1")("Sửa Brochure"),
            Span(f"Chỉnh sửa brochure: {slug}", cls="text-sm text-gray-600"),
        ),
        form,
    )
    
    mock_req = MockRequest(request)
    html_obj = AdminViews.layout(mock_req, "Sửa Brochure", content)
    html_str = _render_html(html_obj)
    response = HttpResponse(html_str, content_type='text/html; charset=utf-8')
    return response
