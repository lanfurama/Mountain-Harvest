"""Admin controller."""
import json
import re
from datetime import datetime
from urllib.parse import urlencode
from starlette.responses import RedirectResponse
from fasthtml.common import *
from api.views.admin_views import AdminViews
from api.repositories.product_repository import ProductRepository
from api.repositories.news_repository import NewsRepository
from api.repositories.hero_repository import HeroRepository
from api.repositories.site_config_repository import SiteConfigRepository
from api.repositories.category_repository import CategoryRepository
from api.repositories.page_repository import PageRepository


class AdminController:
    """Controller for Admin routes."""
    
    PER_PAGE = 10
    
    @staticmethod
    def _build_query_string(params: dict, updates: dict = None) -> str:
        """Build query string."""
        merged = {**params}
        if updates:
            merged.update(updates)
        parts = [f"{k}={v}" for k, v in merged.items() if v]
        return "?" + "&".join(parts) if parts else ""
    
    @staticmethod
    async def index(req):
        """Admin dashboard."""
        from api.db import get_conn
        counts = {"products": 0, "news": 0, "categories": 0, "pages": 0}
        async with get_conn() as conn:
            if conn:
                try:
                    counts["products"] = await conn.fetchval("SELECT COUNT(*) FROM products") or 0
                    counts["news"] = await conn.fetchval("SELECT COUNT(*) FROM news") or 0
                    counts["categories"] = await conn.fetchval("SELECT COUNT(*) FROM categories") or 0
                    counts["pages"] = await conn.fetchval("SELECT COUNT(*) FROM pages") or 0
                except Exception:
                    pass
        stats = [
            (counts["products"], "fa-box", "Sản phẩm", "/admin/products"),
            (counts["news"], "fa-newspaper", "Tin tức", "/admin/news"),
            (counts["categories"], "fa-folder", "Danh mục", "/admin/categories"),
            (counts["pages"], "fa-file-alt", "Trang", "/admin/pages"),
        ]
        cards = []
        for n, icon, label, href in stats:
            cards.append(
                A(href=href, cls="block p-3 rounded border border-[#2F5233]/10 bg-white hover:shadow-md hover:border-[#2F5233]/20 transition")(
                    Div(cls="flex items-center justify-between")(
                        Div(cls="text-3xl font-bold text-[#2F5233]")(str(n)),
                        I(cls=f"fas {icon} text-2xl text-[#2F5233]/40"),
                    ),
                    Div(cls="mt-2 text-sm font-medium text-gray-600")(label),
                )
            )
        quick_actions = Div(cls="mt-8")(
            H2("Thao tác nhanh", cls="text-lg font-semibold text-gray-800 mb-4"),
            Div(cls="flex flex-wrap gap-3")(
                A("+ Thêm sản phẩm", href="/admin/products", cls="inline-flex items-center gap-1.5 px-3 py-1.5 rounded bg-[#E85D04] text-white hover:bg-[#c75003] transition text-sm font-medium"),
                A("+ Thêm tin mới", href="/admin/news/add", cls="inline-flex items-center gap-1.5 px-3 py-1.5 rounded bg-[#2F5233] text-white hover:bg-[#1a331d] transition text-sm font-medium"),
                A("+ Thêm trang", href="/admin/pages", cls="inline-flex items-center gap-1.5 px-3 py-1.5 rounded border border-[#2F5233] text-[#2F5233] hover:bg-[#2F5233]/5 transition text-sm font-medium"),
            ),
        )
        return AdminViews.layout(req, "Dashboard", Div(
            H1("Dashboard", cls="text-2xl font-bold mb-2 text-gray-800"),
            P("Chào mừng đến với CMS Mountain Harvest.", cls="text-gray-600 mb-6"),
            Div(cls="grid grid-cols-2 lg:grid-cols-4 gap-4")(*cards),
            quick_actions,
        ))
    
    @staticmethod
    async def categories(req):
        """Admin categories list."""
        from api.db import get_conn
        async with get_conn() as conn:
            if not conn:
                return AdminViews.layout(req, "Categories", P("Kết nối database để quản lý danh mục.", cls="text-amber-600"))
        rows = await CategoryRepository.get_all_rows()
        add_form = Form(method="post", action="/admin/categories/add", cls="mb-4 p-3 bg-[#F1F0E8]/50 border border-[#2F5233]/20 rounded")(
            H2("Thêm danh mục", cls="text-lg font-bold mb-3 text-gray-800"),
            Div(cls="flex gap-4 items-end")(
                Div(cls="flex-1")(
                    Label("Tên", cls="block text-sm font-medium mb-1 text-gray-700"),
                    Input(name="name", cls="w-full border border-gray-300 rounded px-2 py-1.5 focus:ring-2 focus:ring-[#2F5233] focus:border-[#2F5233]", required=True, placeholder="Tên danh mục"),
                ),
                Div(cls="w-24")(
                    Label("Thứ tự", cls="block text-sm font-medium mb-1 text-gray-700"),
                    Input(name="sort_order", type="number", value="0", cls="w-full border border-gray-300 rounded px-2 py-1.5 focus:ring-2 focus:ring-[#2F5233]"),
                ),
                Button("Thêm", type="submit", cls="px-3 py-1.5 bg-[#E85D04] text-white rounded hover:bg-[#c75003] text-sm font-medium"),
            ),
        )
        rows_html = []
        for r in rows:
            rows_html.append(Tr(cls="hover:bg-[#F1F0E8]/50 transition")(
                Td(r["id"], cls="px-3 py-2 border-t border-[#2F5233]/10 font-mono text-gray-500 text-sm"),
                Td(r["name"], cls="px-3 py-2 border-t border-[#2F5233]/10 font-medium"),
                Td(r.get("sort_order", 0), cls="px-3 py-2 border-t border-[#2F5233]/10 text-gray-600 text-sm"),
                Td(cls="px-3 py-2 border-t border-gray-200 whitespace-nowrap")(
                    A(I(cls="fas fa-edit"), href=f"/admin/categories/{r['id']}/edit", cls="inline-flex items-center gap-1 px-2 py-1 text-blue-600 hover:bg-blue-50 rounded text-sm mr-1"),
                    Form(method="post", action=f"/admin/categories/{r['id']}/delete", cls="inline")(
                        Button(I(cls="fas fa-trash"), type="submit", cls="inline-flex items-center gap-1 px-2 py-1 text-red-600 hover:bg-red-50 rounded text-sm", **{"data-confirm": "Xóa danh mục này?"}),
                    ),
                ),
            ))
        table = Table(cls="w-full border-collapse rounded overflow-hidden")(
            Thead(cls="bg-[#2F5233]/10")(
                Tr(Th("ID", cls="px-3 py-2 text-left text-xs font-semibold text-[#2F5233]"), Th("Tên", cls="px-3 py-2 text-left text-xs font-semibold text-[#2F5233]"), Th("Thứ tự", cls="px-3 py-2 text-left text-xs font-semibold text-[#2F5233]"), Th("Thao tác", cls="px-3 py-2 text-left text-xs font-semibold text-[#2F5233]")),
            ),
            Tbody(*rows_html),
        )
        table_wrapper = Div(cls="overflow-x-auto rounded border border-[#2F5233]/10")(table) if rows_html else Div(cls="text-center py-8 text-gray-500 rounded border border-[#2F5233]/10 bg-white")(
            I(cls="fas fa-folder-open text-4xl mb-4 block text-gray-300"),
            P("Chưa có danh mục nào.", cls="mb-4"),
            Span("Thêm danh mục ở form phía trên.", cls="text-sm"),
        )
        return AdminViews.layout(req, "Categories", Div(H1("Danh mục", cls="text-2xl font-bold mb-4 text-gray-800"), add_form, table_wrapper))
    
    @staticmethod
    async def category_add(req):
        """Add category."""
        if req.method != "POST":
            return RedirectResponse("/admin/categories")
        form = await req.form()
        sort_order = int(form.get("sort_order", 0) or 0)
        await CategoryRepository.create(name=form.get("name", "").strip(), sort_order=sort_order)
        return RedirectResponse("/admin/categories?" + urlencode({"success": "Đã thêm danh mục"}), status_code=303)
    
    @staticmethod
    async def category_edit(req, id: int):
        """Edit category."""
        r = await CategoryRepository.get_by_id(id)
        if not r:
            return RedirectResponse("/admin/categories")
        f = Form(method="post", action=f"/admin/categories/{id}", cls="space-y-4")(
            Div(Label("Tên", cls="block text-sm font-medium text-gray-700"), Input(name="name", value=r["name"], cls="w-full border border-gray-300 rounded px-2 py-1.5 focus:ring-2 focus:ring-[#2F5233] focus:border-[#2F5233]", required=True)),
            Div(Label("Thứ tự", cls="block text-sm font-medium text-gray-700"), Input(name="sort_order", type="number", value=r.get("sort_order", 0), cls="w-full border border-gray-300 rounded px-2 py-1.5 focus:ring-2 focus:ring-[#2F5233]")),
            Button("Lưu", type="submit", cls="px-3 py-1.5 bg-[#2F5233] text-white rounded hover:bg-[#1a331d] text-sm font-medium"),
        )
        return AdminViews.layout(req, "Sửa danh mục", Div(H1("Sửa danh mục", cls="text-2xl font-bold mb-4"), f))
    
    @staticmethod
    async def category_update(req, id: int):
        """Update category."""
        if req.method != "POST":
            return RedirectResponse("/admin/categories")
        form = await req.form()
        sort_order = int(form.get("sort_order", 0) or 0)
        await CategoryRepository.update(id=id, name=form.get("name", "").strip(), sort_order=sort_order)
        return RedirectResponse("/admin/categories?" + urlencode({"success": "Đã cập nhật danh mục"}), status_code=303)
    
    @staticmethod
    async def category_delete(req, id: int):
        """Delete category."""
        if req.method != "POST":
            return RedirectResponse("/admin/categories")
        await CategoryRepository.delete(id)
        return RedirectResponse("/admin/categories?" + urlencode({"success": "Đã xóa danh mục"}), status_code=303)
    
    @staticmethod
    async def products(req):
        """Admin products list."""
        qp = req.query_params
        category = qp.get("category", "").strip()
        search = qp.get("q", "").strip()
        sort = qp.get("sort", "newest")
        page = max(1, int(qp.get("page", 1)))
        per = min(50, max(5, int(qp.get("per_page", AdminController.PER_PAGE))))
        
        from api.db import get_conn
        async with get_conn() as conn:
            if not conn:
                return AdminViews.layout(req, "Products", P("Kết nối database để quản lý sản phẩm.", cls="text-amber-600"))
        
        categories = await CategoryRepository.get_names()
        rows, total = await ProductRepository.search(category=category, search=search, sort=sort, page=page, per_page=per)
        
        total_pages = (total + per - 1) // per if total else 1
        base_params = {"category": category, "q": search, "sort": sort, "per_page": str(per)}
        
        filter_form = Form(method="get", action="/admin/products", cls="flex flex-wrap gap-2 items-end mb-4 p-3 bg-[#F1F0E8]/50 border border-[#2F5233]/10 rounded")(
            Div(cls="flex-1 min-w-[200px]")(
                Label("Tìm kiếm", cls="block text-sm font-medium mb-1 text-gray-700"),
                Input(name="q", value=search, placeholder="Tên sản phẩm...", cls="w-full border border-gray-300 rounded px-2 py-1.5 text-sm focus:ring-2 focus:ring-[#2F5233] focus:border-[#2F5233]"),
            ),
            Div(cls="min-w-[160px]")(
                Label("Danh mục", cls="block text-sm font-medium mb-1 text-gray-700"),
                Select(
                    *([Option("Tất cả", value="")] + [Option(c, value=c, selected=(c == category)) for c in categories]),
                    name="category", cls="w-full border border-gray-300 rounded px-2 py-1.5 text-sm focus:ring-2 focus:ring-[#2F5233]",
                ),
            ),
            Div(cls="min-w-[160px]")(
                Label("Sắp xếp", cls="block text-sm font-medium mb-1 text-gray-700"),
                Select(
                    Option("Mới nhất", value="newest", selected=(sort == "newest")),
                    Option("Cũ nhất", value="oldest", selected=(sort == "oldest")),
                    Option("Giá thấp → cao", value="price_asc", selected=(sort == "price_asc")),
                    Option("Giá cao → thấp", value="price_desc", selected=(sort == "price_desc")),
                    Option("Tên A-Z", value="name", selected=(sort == "name")),
                    name="sort", cls="w-full border border-gray-300 rounded px-2 py-1.5 text-sm",
                ),
            ),
            Input(name="per_page", type="hidden", value=str(per)),
            Button("Lọc", type="submit", cls="px-3 py-1.5 bg-[#2F5233] text-white rounded hover:bg-[#1a331d] text-sm font-medium"),
        )
        
        category_options = [Option("-- Chọn danh mục --", value="")] + [Option(c, value=c) for c in categories]
        add_form = Form(method="post", action="/admin/products/new", cls="mb-4 p-3 bg-[#F1F0E8]/50 border border-[#2F5233]/20 rounded")(
            H2("Thêm sản phẩm", cls="text-lg font-bold mb-3 text-gray-800"),
            Div(cls="grid grid-cols-2 gap-4")(
                Div(Label("Tên", cls="block text-sm font-medium mb-1"), Input(name="name", cls="w-full border rounded px-2 py-1", required=True)),
                Div(Label("Slug (URL, để trống = auto từ tên)"), Input(name="slug", cls="w-full border rounded px-2 py-1", placeholder="ca-chua-cherry-huu-co")),
                Div(Label("Danh mục", cls="block text-sm font-medium mb-1"), Select(*category_options, name="category", cls="w-full border rounded px-2 py-1", required=True)),
                Div(Label("Giá (VNĐ)", cls="block text-sm font-medium mb-1"), Input(name="price", type="number", cls="w-full border rounded px-2 py-1", required=True)),
                Div(Label("Giá gốc (để trống nếu không)"), Input(name="original_price", type="number", cls="w-full border rounded px-2 py-1")),
                Div(Label("Đơn vị (vd: /500g)"), Input(name="unit", cls="w-full border rounded px-2 py-1", placeholder="/500g")),
                Div(Label("Ảnh URL"), Input(name="image", type="url", cls="w-full border rounded px-2 py-1")),
                Div(Label("Tags (phân cách bởi dấu phẩy)"), Input(name="tags", cls="w-full border rounded px-2 py-1", placeholder="Organic, Best Seller")),
                Div(Label("Giảm giá (vd: -15%)"), Input(name="discount", cls="w-full border rounded px-2 py-1")),
                Div(cls="col-span-2 flex gap-4 items-center")(
                    Div(cls="flex items-center gap-2")(Input(name="is_hot", type="checkbox", value="1"), Label("Sản phẩm hot")),
                    Div(Label("Rating"), Input(name="rating", type="number", step="0.1", value="0", cls="w-20 border rounded px-2 py-1")),
                    Div(Label("Reviews"), Input(name="reviews", type="number", value="0", cls="w-20 border rounded px-2 py-1")),
                    Div(Label("Thứ tự"), Input(name="sort_order", type="number", value="0", cls="w-20 border rounded px-2 py-1")),
                ),
                Div(cls="col-span-2")(Label("Mô tả"), Textarea(name="description", cls="w-full border rounded px-2 py-1", rows=3)),
            ),
            Div(cls="border-t pt-4 mt-4")(
                H3("SEO Settings", cls="text-lg font-bold mb-3 text-gray-800"),
                Div(Label("Meta Title", cls="block text-sm font-medium mb-1"), Input(name="meta_title", placeholder="SEO title", cls="w-full border rounded px-2 py-1")),
                Div(Label("Meta Description", cls="block text-sm font-medium mb-1"), Textarea(name="meta_description", placeholder="SEO description", cls="w-full border rounded px-2 py-1", rows=2)),
                Div(cls="grid grid-cols-3 gap-3")(
                    Div(Label("H1 Custom", cls="block text-sm font-medium mb-1"), Input(name="h1_custom", placeholder="H1", cls="w-full border rounded px-2 py-1")),
                    Div(Label("H2 Custom", cls="block text-sm font-medium mb-1"), Input(name="h2_custom", placeholder="H2", cls="w-full border rounded px-2 py-1")),
                    Div(Label("H3 Custom", cls="block text-sm font-medium mb-1"), Input(name="h3_custom", placeholder="H3", cls="w-full border rounded px-2 py-1")),
                ),
            ),
            Button("Thêm", type="submit", cls="mt-2 px-3 py-1.5 bg-[#E85D04] text-white rounded hover:bg-[#c75003] text-sm font-medium"),
        )
        
        rows_html = []
        for r in rows:
            rows_html.append(Tr(cls="hover:bg-[#F1F0E8]/50 transition")(
                Td(r["id"], cls="px-3 py-2 border-t border-[#2F5233]/10 font-mono text-gray-500 text-sm"),
                Td(r["name"], cls="px-3 py-2 border-t border-[#2F5233]/10 font-medium"),
                Td(r["category"], cls="px-3 py-2 border-t border-[#2F5233]/10 text-gray-600 text-sm"),
                Td(f"{r['price']:,}đ", cls="px-3 py-2 border-t border-[#2F5233]/10 font-medium text-gray-800"),
                Td(Img(src=r["image"] or "", cls="w-10 h-10 object-cover rounded border") if r["image"] else Span("-", cls="text-gray-400"), cls="px-3 py-2 border-t border-[#2F5233]/10"),
                Td(cls="px-3 py-2 border-t border-gray-200 whitespace-nowrap")(
                    A(I(cls="fas fa-edit"), href=f"/admin/products/{r['id']}/edit", cls="inline-flex items-center gap-1 px-2 py-1 text-blue-600 hover:bg-blue-50 rounded text-sm mr-1"),
                    Form(method="post", action=f"/admin/products/{r['id']}/delete", cls="inline")(
                        Button(I(cls="fas fa-trash"), type="submit", cls="inline-flex items-center gap-1 px-2 py-1 text-red-600 hover:bg-red-50 rounded text-sm", **{"data-confirm": "Xóa sản phẩm này?"}),
                    ),
                ),
            ))
        table = Table(cls="w-full border-collapse")(
            Thead(cls="bg-[#2F5233]/10")(
                Tr(Th("ID", cls="px-3 py-2 text-left text-xs font-semibold text-[#2F5233]"), Th("Tên", cls="px-3 py-2 text-left text-xs font-semibold text-[#2F5233]"), Th("Danh mục", cls="px-3 py-2 text-left text-xs font-semibold text-[#2F5233]"), Th("Giá", cls="px-3 py-2 text-left text-xs font-semibold text-[#2F5233]"), Th("Ảnh", cls="px-3 py-2 text-left text-xs font-semibold text-[#2F5233]"), Th("Thao tác", cls="px-3 py-2 text-left text-xs font-semibold text-[#2F5233]")),
            ),
            Tbody(*rows_html),
        )
        
        pagination = []
        if total_pages > 1:
            for p in range(1, total_pages + 1):
                qs = AdminController._build_query_string(base_params, {"page": str(p)})
                if p == page:
                    pagination.append(Span(str(p), cls="inline-flex items-center justify-center w-8 h-8 bg-[#2F5233] text-white rounded font-medium text-sm"))
                else:
                    pagination.append(A(str(p), href=f"/admin/products{qs}", cls="inline-flex items-center justify-center w-8 h-8 border border-[#2F5233]/20 rounded hover:bg-[#2F5233]/5 text-gray-700 text-sm"))
            pagination_html = Nav(cls="flex items-center gap-2 mt-4")(
                A(I(cls="fas fa-chevron-left"), href=f"/admin/products{AdminController._build_query_string(base_params, {'page': str(max(1, page - 1))})}", cls="p-1.5 rounded border border-[#2F5233]/20 hover:bg-[#2F5233]/5" + (" opacity-50 pointer-events-none" if page <= 1 else "")),
                *pagination,
                A(I(cls="fas fa-chevron-right"), href=f"/admin/products{AdminController._build_query_string(base_params, {'page': str(min(total_pages, page + 1))})}", cls="p-1.5 rounded border border-[#2F5233]/20 hover:bg-[#2F5233]/5" + (" opacity-50 pointer-events-none" if page >= total_pages else "")),
            )
        else:
            pagination_html = Div()
        
        header = Div(cls="flex flex-wrap justify-between items-center gap-4 mb-4")(
            H1("Sản phẩm", cls="text-2xl font-bold text-gray-800"),
            Span(f"{total} sản phẩm" + (f" • Trang {page}/{total_pages}" if total_pages > 1 else ""), cls="text-sm text-gray-500"),
        )
        return AdminViews.layout(req, "Products", Div(header, filter_form, add_form, Div(cls="overflow-x-auto")(table), pagination_html))
    
    @staticmethod
    async def product_new(req):
        """Create new product."""
        form = await req.form()
        tags_raw = form.get("tags") or ""
        tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
        from api.views.product_views import _slugify
        slug = (form.get("slug") or "").strip()
        if not slug:
            slug = _slugify(form.get("name", ""))
        await ProductRepository.create(
            name=form.get("name", ""),
            slug=slug or None,
            category=form.get("category", ""),
            price=int(form.get("price", 0) or 0),
            original_price=int(form.get("original_price")) if form.get("original_price") else None,
            unit=form.get("unit") or None,
            image=form.get("image") or None,
            description=form.get("description") or None,
            tags=tags,
            is_hot=bool(form.get("is_hot")),
            discount=form.get("discount") or None,
            rating=float(form.get("rating", 0) or 0),
            reviews=int(form.get("reviews", 0) or 0),
            sort_order=int(form.get("sort_order", 0) or 0),
            meta_title=form.get("meta_title") or None,
            meta_description=form.get("meta_description") or None,
            h1_custom=form.get("h1_custom") or None,
            h2_custom=form.get("h2_custom") or None,
            h3_custom=form.get("h3_custom") or None,
        )
        return RedirectResponse("/admin/products?" + urlencode({"success": "Đã thêm sản phẩm"}), status_code=303)
    
    @staticmethod
    async def product_edit(req, id: int):
        """Edit product."""
        from api.db import get_conn
        async with get_conn() as conn:
            if not conn:
                return RedirectResponse("/admin/products")
        
        r = await ProductRepository.get_by_id_for_edit(id)
        if not r:
            return RedirectResponse("/admin/products")
        categories = await CategoryRepository.get_names()
        cur_cat = r.get("category", "")
        category_options = [Option(c, value=c, selected=(c == cur_cat)) for c in categories]
        if cur_cat and cur_cat not in categories:
            category_options.insert(0, Option(cur_cat, value=cur_cat, selected=True))
        tags_str = ",".join(r["tags"] or []) if isinstance(r["tags"], list) else ""
        f = Form(method="post", action=f"/admin/products/{id}", cls="space-y-4")(
            Div(Label("Tên"), Input(name="name", value=r["name"], cls="w-full border rounded px-2 py-1", required=True)),
            Div(Label("Slug (URL)"), Input(name="slug", value=r.get("slug") or "", cls="w-full border rounded px-2 py-1", placeholder="ca-chua-cherry")),
            Div(Label("Danh mục"), Select(*category_options, name="category", cls="w-full border rounded px-2 py-1")),
            Div(Label("Giá"), Input(name="price", type="number", value=r["price"], cls="w-full border rounded px-2 py-1")),
            Div(Label("Giá gốc (để trống nếu không)"), Input(name="original_price", type="number", value=r["original_price"] or "", cls="w-full border rounded px-2 py-1")),
            Div(Label("Đơn vị (vd: /500g)"), Input(name="unit", value=r["unit"] or "", cls="w-full border rounded px-2 py-1")),
            Div(Label("Ảnh URL"), Input(name="image", type="url", value=r["image"] or "", cls="w-full border rounded px-2 py-1")),
            Div(Label("Mô tả"), Textarea(name="description", cls="w-full border rounded px-2 py-1", rows=4)(r["description"] or "")),
            Div(Label("Tags (phân cách bởi dấu phẩy)"), Input(name="tags", value=tags_str, cls="w-full border rounded px-2 py-1")),
            Div(cls="flex flex-wrap gap-4 items-center")(
                Div(cls="flex items-center gap-2")(Input(name="is_hot", type="checkbox", value="1", **({"checked": True} if r.get("is_hot") else {})), Label("Sản phẩm hot")),
                Div(Label("Giảm giá", cls="block text-sm"), Input(name="discount", value=r.get("discount") or "", cls="w-24 border rounded px-2 py-1")),
                Div(Label("Rating", cls="block text-sm"), Input(name="rating", type="number", step="0.1", value=r.get("rating") or "0", cls="w-20 border rounded px-2 py-1")),
                Div(Label("Reviews", cls="block text-sm"), Input(name="reviews", type="number", value=r.get("reviews") or "0", cls="w-20 border rounded px-2 py-1")),
                Div(Label("Thứ tự", cls="block text-sm"), Input(name="sort_order", type="number", value=r.get("sort_order") or "0", cls="w-20 border rounded px-2 py-1")),
            ),
            Div(cls="border-t pt-4 mt-4")(
                H3("SEO Settings", cls="text-lg font-bold mb-3 text-gray-800"),
                Div(Label("Meta Title", cls="block text-sm font-medium mb-1"), Input(name="meta_title", value=r.get("meta_title") or "", placeholder="SEO title", cls="w-full border rounded px-2 py-1")),
                Div(Label("Meta Description", cls="block text-sm font-medium mb-1"), Textarea(name="meta_description", value=r.get("meta_description") or "", placeholder="SEO description", cls="w-full border rounded px-2 py-1", rows=2)),
                Div(cls="grid grid-cols-3 gap-3")(
                    Div(Label("H1 Custom", cls="block text-sm font-medium mb-1"), Input(name="h1_custom", value=r.get("h1_custom") or "", placeholder="H1", cls="w-full border rounded px-2 py-1")),
                    Div(Label("H2 Custom", cls="block text-sm font-medium mb-1"), Input(name="h2_custom", value=r.get("h2_custom") or "", placeholder="H2", cls="w-full border rounded px-2 py-1")),
                    Div(Label("H3 Custom", cls="block text-sm font-medium mb-1"), Input(name="h3_custom", value=r.get("h3_custom") or "", placeholder="H3", cls="w-full border rounded px-2 py-1")),
                ),
            ),
            Button("Lưu", type="submit", cls="px-3 py-1.5 bg-[#2F5233] text-white rounded hover:bg-[#1a331d] text-sm font-medium"),
        )
        return AdminViews.layout(req, "Sửa sản phẩm", Div(H1("Sửa sản phẩm", cls="text-2xl font-bold mb-4"), f))
    
    @staticmethod
    async def product_update(req, id: int):
        """Update product."""
        if req.method != "POST":
            return RedirectResponse("/admin/products")
        form = await req.form()
        tags_raw = form.get("tags") or ""
        tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
        from api.views.product_views import _slugify
        slug = (form.get("slug") or "").strip()
        if not slug:
            slug = _slugify(form.get("name", ""))
        await ProductRepository.update(
            id=id,
            name=form.get("name"),
            slug=slug or None,
            category=form.get("category"),
            price=int(form.get("price") or 0),
            original_price=int(form.get("original_price")) if form.get("original_price") else None,
            unit=form.get("unit") or None,
            image=form.get("image") or None,
            description=form.get("description") or None,
            tags=tags,
            is_hot=bool(form.get("is_hot")),
            discount=form.get("discount") or None,
            rating=float(form.get("rating", 0) or 0),
            reviews=int(form.get("reviews", 0) or 0),
            sort_order=int(form.get("sort_order", 0) or 0),
            meta_title=form.get("meta_title") or None,
            meta_description=form.get("meta_description") or None,
            h1_custom=form.get("h1_custom") or None,
            h2_custom=form.get("h2_custom") or None,
            h3_custom=form.get("h3_custom") or None,
        )
        return RedirectResponse("/admin/products?" + urlencode({"success": "Đã cập nhật sản phẩm"}), status_code=303)
    
    @staticmethod
    async def product_delete(req, id: int):
        """Delete product."""
        if req.method != "POST":
            return RedirectResponse("/admin/products")
        await ProductRepository.delete(id)
        return RedirectResponse("/admin/products?" + urlencode({"success": "Đã xóa sản phẩm"}), status_code=303)
    
    @staticmethod
    async def news(req):
        """Admin news list."""
        qp = req.query_params
        search = qp.get("q", "").strip()
        page = max(1, int(qp.get("page", 1)))
        per = min(50, max(5, int(qp.get("per_page", AdminController.PER_PAGE))))
        
        from api.db import get_conn
        async with get_conn() as conn:
            if not conn:
                return AdminViews.layout(req, "News", P("Kết nối database để quản lý tin tức.", cls="text-amber-600"))
        
        rows, total = await NewsRepository.search(search=search, page=page, per_page=per)
        
        total_pages = (total + per - 1) // per if total else 1
        base_params = {"q": search, "per_page": str(per)}
        
        filter_form = Form(method="get", action="/admin/news", cls="flex flex-wrap gap-2 items-end mb-4 p-3 bg-gray-50 rounded")(
            Div(cls="flex-1 min-w-[240px]")(
                Label("Tìm kiếm", cls="block text-sm font-medium mb-1"),
                Input(name="q", value=search, placeholder="Tiêu đề, nội dung hoặc tác giả...", cls="w-full border border-gray-300 rounded px-2 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"),
            ),
            Input(name="per_page", type="hidden", value=str(per)),
            Button("Lọc", type="submit", cls="px-3 py-1.5 bg-[#2F5233] text-white rounded hover:bg-[#1a331d] text-sm font-medium"),
        )
        
        rows_html = []
        for r in rows:
            rows_html.append(Tr(cls="hover:bg-gray-50")(
                Td(r["id"], cls="px-3 py-2 border-t border-gray-200 font-mono text-gray-500 text-sm"),
                Td(r["title"], cls="px-3 py-2 border-t border-gray-200 font-medium"),
                Td(r["date"] or "-", cls="px-3 py-2 border-t border-gray-200 text-gray-600 text-sm"),
                Td(r["author"] or "-", cls="px-3 py-2 border-t border-gray-200 text-gray-600 text-sm"),
                Td(Img(src=r["image"] or "", cls="w-10 h-10 object-cover rounded border") if r.get("image") else Span("-", cls="text-gray-400"), cls="px-3 py-2 border-t border-gray-200"),
                Td(cls="px-3 py-2 border-t border-gray-200 whitespace-nowrap")(
                    A(I(cls="fas fa-edit"), href=f"/admin/news/{r['id']}/edit", cls="inline-flex items-center gap-1 px-2 py-1 text-blue-600 hover:bg-blue-50 rounded text-sm mr-1"),
                    Form(method="post", action=f"/admin/news/{r['id']}/delete", cls="inline")(
                        Button(I(cls="fas fa-trash"), type="submit", cls="inline-flex items-center gap-1 px-2 py-1 text-red-600 hover:bg-red-50 rounded text-sm", **{"data-confirm": "Xóa tin này?"}),
                    ),
                ),
            ))
        table = Table(cls="w-full border-collapse")(
            Thead(cls="bg-[#2F5233]/10")(
                Tr(Th("ID", cls="px-3 py-2 text-left text-xs font-semibold text-[#2F5233]"), Th("Tiêu đề", cls="px-3 py-2 text-left text-xs font-semibold text-[#2F5233]"), Th("Ngày", cls="px-3 py-2 text-left text-xs font-semibold text-[#2F5233]"), Th("Tác giả", cls="px-3 py-2 text-left text-xs font-semibold text-[#2F5233]"), Th("Ảnh", cls="px-3 py-2 text-left text-xs font-semibold text-[#2F5233]"), Th("Thao tác", cls="px-3 py-2 text-left text-xs font-semibold text-[#2F5233]")),
            ),
            Tbody(*rows_html),
        )
        
        pagination = []
        if total_pages > 1:
            for p in range(1, total_pages + 1):
                qs = AdminController._build_query_string(base_params, {"page": str(p)})
                if p == page:
                    pagination.append(Span(str(p), cls="inline-flex items-center justify-center w-8 h-8 bg-[#2F5233] text-white rounded font-medium text-sm"))
                else:
                    pagination.append(A(str(p), href=f"/admin/news{qs}", cls="inline-flex items-center justify-center w-8 h-8 border border-gray-300 rounded hover:bg-gray-100 text-gray-700 text-sm"))
            pagination_html = Nav(cls="flex items-center gap-2 mt-4")(
                A(I(cls="fas fa-chevron-left"), href=f"/admin/news{AdminController._build_query_string(base_params, {'page': str(max(1, page - 1))})}", cls="p-1.5 rounded border hover:bg-gray-100" + (" opacity-50 pointer-events-none" if page <= 1 else "")),
                *pagination,
                A(I(cls="fas fa-chevron-right"), href=f"/admin/news{AdminController._build_query_string(base_params, {'page': str(min(total_pages, page + 1))})}", cls="p-1.5 rounded border hover:bg-gray-100" + (" opacity-50 pointer-events-none" if page >= total_pages else "")),
            )
        else:
            pagination_html = Div()
        
        header = Div(cls="flex flex-wrap justify-between items-center gap-4 mb-4")(
            H1("Tin tức", cls="text-2xl font-bold text-gray-800"),
            Div(cls="flex items-center gap-3")(
                A("+ Thêm tin mới", href="/admin/news/add", cls="px-3 py-1.5 bg-[#E85D04] text-white rounded hover:bg-[#c75003] text-sm font-medium inline-flex items-center gap-2"),
                Span(f"{total} tin" + (f" • Trang {page}/{total_pages}" if total_pages > 1 else ""), cls="text-sm text-gray-500"),
            ),
        )
        return AdminViews.layout(req, "News", Div(header, filter_form, Div(cls="overflow-x-auto")(table), pagination_html))
    
    @staticmethod
    async def news_add(req):
        """Add news."""
        if req.method == "POST":
            form = await req.form()
            date_value = form.get("date")
            if date_value:
                try:
                    date_obj = datetime.strptime(date_value, "%Y-%m-%d")
                    date_value = date_obj.strftime("%d/%m/%Y")
                except:
                    pass
            title = form.get("title")
            content = form.get("content") or ""
            meta_title = (form.get("meta_title") or "").strip() or title
            content_text = re.sub(r'<[^>]+>', '', content).strip()
            meta_description = (form.get("meta_description") or "").strip() or (content_text[:100] if content_text else None)
            from api.views.product_views import _slugify
            slug = (form.get("slug") or "").strip() or _slugify(title)
            await NewsRepository.create(
                title=title,
                slug=slug or None,
                image=form.get("image") or None,
                content=content,
                author=form.get("author") or "Mountain Harvest",
                date=date_value,
                meta_title=meta_title,
                meta_description=meta_description,
                h1_custom=form.get("h1_custom") or None,
                h2_custom=form.get("h2_custom") or None,
                h3_custom=form.get("h3_custom") or None,
            )
            return RedirectResponse("/admin/news?" + urlencode({"success": "Đã thêm tin mới"}), status_code=303)
        
        current_date_value = datetime.now().strftime("%Y-%m-%d")
        
        form = Form(method="post", action="/admin/news/add", cls="space-y-3")(
            Div(
                Label("Tiêu đề", cls="block text-sm font-medium mb-1 text-gray-700"),
                Input(name="title", cls="w-full border border-gray-300 rounded px-2 py-1.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500", required=True),
            ),
            Div(cls="grid grid-cols-2 gap-3")(
                Div(
                    Label("Tác giả", cls="block text-sm font-medium mb-1 text-gray-700"),
                    Input(name="author", value="Mountain Harvest", cls="w-full border border-gray-300 rounded px-2 py-1.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"),
                ),
                Div(
                    Label("Ngày tạo", cls="block text-sm font-medium mb-1 text-gray-700"),
                    Input(name="date", type="date", value=current_date_value, cls="w-full border border-gray-300 rounded px-2 py-1.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"),
                ),
            ),
            Div(
                Label("Ảnh URL", cls="block text-sm font-medium mb-1 text-gray-700"),
                Input(name="image", type="url", cls="w-full border border-gray-300 rounded px-2 py-1.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"),
            ),
            Div(
                Label("Slug (URL, để trống = auto từ tiêu đề)", cls="block text-sm font-medium mb-1 text-gray-700"),
                Input(name="slug", placeholder="mua-thu-hoach-bo-sap", cls="w-full border border-gray-300 rounded px-2 py-1.5 focus:ring-2 focus:ring-blue-500"),
            ),
            Div(cls="border-t pt-4 mt-4")(
                H3("SEO", cls="text-lg font-bold mb-2 text-gray-700"),
                Div(Label("Meta Title (để trống = dùng tiêu đề)", cls="block text-sm font-medium mb-1"), Input(name="meta_title", placeholder="SEO title", cls="w-full border border-gray-300 rounded px-2 py-1.5")),
                Div(Label("Meta Description (để trống = 100 ký tự đầu nội dung)", cls="block text-sm font-medium mb-1"), Textarea(name="meta_description", placeholder="SEO description", cls="w-full border border-gray-300 rounded px-2 py-1.5", rows=2)),
            ),
            Div(cls="grid grid-cols-3 gap-3")(
                Div(Label("H1 Custom", cls="block text-sm font-medium mb-1 text-gray-700"), Input(name="h1_custom", placeholder="H1 SEO", cls="w-full border border-gray-300 rounded px-2 py-1.5 focus:ring-2 focus:ring-blue-500")),
                Div(Label("H2 Custom", cls="block text-sm font-medium mb-1 text-gray-700"), Input(name="h2_custom", placeholder="H2 SEO", cls="w-full border border-gray-300 rounded px-2 py-1.5 focus:ring-2 focus:ring-blue-500")),
                Div(Label("H3 Custom", cls="block text-sm font-medium mb-1 text-gray-700"), Input(name="h3_custom", placeholder="H3 SEO", cls="w-full border border-gray-300 rounded px-2 py-1.5 focus:ring-2 focus:ring-blue-500")),
            ),
            Div(
                Label("Nội dung", cls="block text-sm font-medium mb-1 text-gray-700"),
                Div(id="news-content-editor", cls="bg-white", style="height: 400px;"),
                Textarea(name="content", id="news-content", cls="hidden"),
            ),
            Div(cls="flex gap-2")(
                Button("Lưu", type="submit", cls="px-4 py-1.5 bg-blue-600 text-white rounded hover:bg-blue-700 font-medium text-sm"),
                A("Hủy", href="/admin/news", cls="px-4 py-1.5 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 font-medium text-sm"),
            ),
        )
        return AdminViews.layout(req, "Thêm tin mới", Div(H1("Thêm tin mới", cls="text-2xl font-bold mb-6 text-gray-800"), form), include_editor=True)
    
    @staticmethod
    async def news_edit(req, id: int):
        """Edit news."""
        from api.db import get_conn
        async with get_conn() as conn:
            if not conn:
                return RedirectResponse("/admin/news")
        
        r = await NewsRepository.get_by_id_for_edit(id)
        if not r:
            return RedirectResponse("/admin/news")
        
        date_value = r["date"] or ""
        if date_value:
            try:
                date_obj = datetime.strptime(date_value, "%d/%m/%Y")
                date_value = date_obj.strftime("%Y-%m-%d")
            except:
                pass
        
        f = Form(method="post", action=f"/admin/news/{id}", cls="space-y-4")(
            Div(
                Label("Tiêu đề", cls="block text-sm font-medium mb-1 text-gray-700"),
                Input(name="title", value=r["title"] or "", cls="w-full border border-gray-300 rounded px-2 py-1.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"),
            ),
            Div(cls="grid grid-cols-2 gap-4")(
                Div(
                    Label("Tác giả", cls="block text-sm font-medium mb-1 text-gray-700"),
                    Input(name="author", value=r["author"] or "", cls="w-full border border-gray-300 rounded px-2 py-1.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"),
                ),
                Div(
                    Label("Ngày", cls="block text-sm font-medium mb-1 text-gray-700"),
                    Input(name="date", type="date", value=date_value, cls="w-full border border-gray-300 rounded px-2 py-1.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"),
                ),
            ),
            Div(
                Label("Ảnh URL", cls="block text-sm font-medium mb-1 text-gray-700"),
                Input(name="image", value=r["image"] or "", cls="w-full border border-gray-300 rounded px-2 py-1.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"),
            ),
            Div(
                Label("Slug (URL)", cls="block text-sm font-medium mb-1 text-gray-700"),
                Input(name="slug", value=r.get("slug") or "", placeholder="mua-thu-hoach-bo-sap", cls="w-full border border-gray-300 rounded px-2 py-1.5 focus:ring-2 focus:ring-blue-500"),
            ),
            Div(cls="border-t pt-4")(H3("SEO", cls="text-lg font-bold mb-2 text-gray-700"),
                Div(Label("Meta Title", cls="block text-sm font-medium mb-1"), Input(name="meta_title", value=r.get("meta_title") or "", placeholder="SEO title", cls="w-full border border-gray-300 rounded px-2 py-1.5")),
                Div(Label("Meta Description", cls="block text-sm font-medium mb-1"), Textarea(name="meta_description", value=r.get("meta_description") or "", placeholder="SEO description", cls="w-full border border-gray-300 rounded px-2 py-1.5", rows=2)),
            ),
            Div(cls="grid grid-cols-3 gap-4")(
                Div(Label("H1 Custom", cls="block text-sm font-medium mb-1 text-gray-700"), Input(name="h1_custom", value=r.get("h1_custom") or "", placeholder="H1 SEO", cls="w-full border border-gray-300 rounded px-2 py-1.5 focus:ring-2 focus:ring-blue-500")),
                Div(Label("H2 Custom", cls="block text-sm font-medium mb-1 text-gray-700"), Input(name="h2_custom", value=r.get("h2_custom") or "", placeholder="H2 SEO", cls="w-full border border-gray-300 rounded px-2 py-1.5 focus:ring-2 focus:ring-blue-500")),
                Div(Label("H3 Custom", cls="block text-sm font-medium mb-1 text-gray-700"), Input(name="h3_custom", value=r.get("h3_custom") or "", placeholder="H3 SEO", cls="w-full border border-gray-300 rounded px-2 py-1.5 focus:ring-2 focus:ring-blue-500")),
            ),
            Div(
                Label("Nội dung", cls="block text-sm font-medium mb-1 text-gray-700"),
                Div(id="news-content-editor", cls="bg-white", style="height: 400px;")(r["content"] or ""),
                Textarea(name="content", id="news-content", cls="hidden")(r["content"] or ""),
            ),
            Div(cls="flex gap-3")(
                Button("Lưu", type="submit", cls="px-4 py-1.5 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm font-medium"),
                A("Hủy", href="/admin/news", cls="px-4 py-1.5 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 text-sm font-medium"),
            ),
        )
        return AdminViews.layout(req, "Sửa tin", Div(H1("Sửa tin", cls="text-2xl font-bold mb-6 text-gray-800"), f), include_editor=True)
    
    @staticmethod
    async def news_update(req, id: int):
        """Update news."""
        if req.method != "POST":
            return RedirectResponse("/admin/news")
        form = await req.form()
        date_value = form.get("date")
        if date_value:
            try:
                date_obj = datetime.strptime(date_value, "%Y-%m-%d")
                date_value = date_obj.strftime("%d/%m/%Y")
            except:
                pass
        title = form.get("title")
        content = form.get("content") or ""
        meta_title = (form.get("meta_title") or "").strip() or title
        content_text = re.sub(r'<[^>]+>', '', content).strip()
        meta_description = (form.get("meta_description") or "").strip() or (content_text[:100] if content_text else None)
        from api.views.product_views import _slugify
        slug = (form.get("slug") or "").strip() or _slugify(title)
        await NewsRepository.update(
            id=id,
            title=title,
            slug=slug or None,
            date=date_value or None,
            image=form.get("image") or None,
            content=content,
            author=form.get("author") or None,
            meta_title=meta_title,
            meta_description=meta_description,
            h1_custom=form.get("h1_custom") or None,
            h2_custom=form.get("h2_custom") or None,
            h3_custom=form.get("h3_custom") or None,
        )
        return RedirectResponse("/admin/news?" + urlencode({"success": "Đã cập nhật tin"}), status_code=303)
    
    @staticmethod
    async def news_delete(req, id: int):
        """Delete news."""
        if req.method != "POST":
            return RedirectResponse("/admin/news")
        await NewsRepository.delete(id)
        return RedirectResponse("/admin/news?" + urlencode({"success": "Đã xóa tin"}), status_code=303)
    
    @staticmethod
    async def pages(req):
        """Admin pages list."""
        rows = await PageRepository.get_all()
        add_form = Form(method="post", action="/admin/pages/add", cls="mb-4 p-3 bg-green-50 border border-green-200 rounded")(
            H2("Thêm trang", cls="text-lg font-bold mb-3 text-gray-800"),
            Div(cls="grid grid-cols-2 gap-4")(
                Div(Label("Slug (URL)", cls="block text-sm font-medium mb-1"), Input(name="slug", cls="w-full border rounded px-2 py-1", required=True, placeholder="gioi-thieu")),
                Div(Label("Tiêu đề", cls="block text-sm font-medium mb-1"), Input(name="title", cls="w-full border rounded px-2 py-1", required=True)),
                Div(cls="col-span-2")(Label("Nội dung"), Textarea(name="content", cls="w-full border rounded px-2 py-1", rows=6)),
                Div(Label("Meta Title"), Input(name="meta_title", cls="w-full border rounded px-2 py-1")),
                Div(Label("Meta Description"), Textarea(name="meta_description", cls="w-full border rounded px-2 py-1", rows=2)),
                Div(Label("Thứ tự"), Input(name="sort_order", type="number", value="0", cls="w-24 border rounded px-2 py-1")),
            ),
            Button("Thêm", type="submit", cls="mt-2 px-3 py-1.5 bg-[#E85D04] text-white rounded hover:bg-[#c75003] text-sm"),
        )
        rows_html = []
        for r in rows:
            rows_html.append(Tr(cls="hover:bg-gray-50")(
                Td(r["id"], cls="px-3 py-2 border-t border-gray-200 font-mono text-sm"),
                Td(r["slug"], cls="px-3 py-2 border-t border-gray-200 font-medium"),
                Td(r["title"], cls="px-3 py-2 border-t border-gray-200"),
                Td(cls="px-3 py-2 border-t border-gray-200 whitespace-nowrap")(
                    A(I(cls="fas fa-external-link-alt"), href=f"/p/{r['slug']}", target="_blank", cls="px-2 py-1 text-blue-600 hover:bg-blue-50 rounded text-sm mr-1"),
                    A(I(cls="fas fa-edit"), href=f"/admin/pages/{r['id']}/edit", cls="inline-flex items-center gap-1 px-2 py-1 text-blue-600 hover:bg-blue-50 rounded text-sm mr-1"),
                    Form(method="post", action=f"/admin/pages/{r['id']}/delete", cls="inline")(
                        Button(I(cls="fas fa-trash"), type="submit", cls="inline-flex items-center gap-1 px-2 py-1 text-red-600 hover:bg-red-50 rounded text-sm", **{"data-confirm": "Xóa trang này?"}),
                    ),
                ),
            ))
        table = Table(cls="w-full border-collapse")(
            Thead(cls="bg-[#2F5233]/10")(
                Tr(Th("ID", cls="px-3 py-2 text-left text-xs font-semibold text-[#2F5233]"), Th("Slug", cls="px-3 py-2 text-left text-xs font-semibold text-[#2F5233]"), Th("Tiêu đề", cls="px-3 py-2 text-left text-xs font-semibold text-[#2F5233]"), Th("Thao tác", cls="px-3 py-2 text-left text-xs font-semibold text-[#2F5233]")),
            ),
            Tbody(*rows_html),
        )
        return AdminViews.layout(req, "Pages", Div(H1("Trang tĩnh", cls="text-2xl font-bold mb-4 text-gray-800"), add_form, Div(cls="overflow-x-auto")(table)))
    
    @staticmethod
    async def page_add(req):
        """Add page."""
        if req.method != "POST":
            return RedirectResponse("/admin/pages")
        form = await req.form()
        sort_order = int(form.get("sort_order", 0) or 0)
        await PageRepository.create(
            slug=(form.get("slug") or "").strip(),
            title=(form.get("title") or "").strip(),
            content=form.get("content") or None,
            meta_title=(form.get("meta_title") or "").strip() or None,
            meta_description=(form.get("meta_description") or "").strip() or None,
            sort_order=sort_order,
        )
        return RedirectResponse("/admin/pages?" + urlencode({"success": "Đã thêm trang"}), status_code=303)
    
    @staticmethod
    async def page_edit(req, id: int):
        """Edit page."""
        r = await PageRepository.get_by_id(id)
        if not r:
            return RedirectResponse("/admin/pages")
        f = Form(method="post", action=f"/admin/pages/{id}", cls="space-y-4")(
            Div(Label("Slug (URL)"), Input(name="slug", value=r["slug"], cls="w-full border rounded px-2 py-1", required=True)),
            Div(Label("Tiêu đề"), Input(name="title", value=r["title"], cls="w-full border rounded px-2 py-1", required=True)),
            Div(Label("Nội dung"), Textarea(name="content", cls="w-full border rounded px-2 py-1", rows=10)(r.get("content") or "")),
            Div(Label("Meta Title"), Input(name="meta_title", value=r.get("meta_title") or "", cls="w-full border rounded px-2 py-1")),
            Div(Label("Meta Description"), Textarea(name="meta_description", cls="w-full border rounded px-2 py-1", rows=2)(r.get("meta_description") or "")),
            Div(Label("Thứ tự"), Input(name="sort_order", type="number", value=r.get("sort_order", 0), cls="w-24 border rounded px-2 py-1")),
            Button("Lưu", type="submit", cls="px-3 py-1.5 bg-[#2F5233] text-white rounded hover:bg-[#1a331d] text-sm font-medium"),
        )
        return AdminViews.layout(req, "Sửa trang", Div(H1("Sửa trang", cls="text-2xl font-bold mb-4"), f))
    
    @staticmethod
    async def page_update(req, id: int):
        """Update page."""
        if req.method != "POST":
            return RedirectResponse("/admin/pages")
        form = await req.form()
        sort_order = int(form.get("sort_order", 0) or 0)
        await PageRepository.update(
            id=id,
            slug=(form.get("slug") or "").strip(),
            title=(form.get("title") or "").strip(),
            content=form.get("content") or None,
            meta_title=(form.get("meta_title") or "").strip() or None,
            meta_description=(form.get("meta_description") or "").strip() or None,
            sort_order=sort_order,
        )
        return RedirectResponse("/admin/pages?" + urlencode({"success": "Đã cập nhật trang"}), status_code=303)
    
    @staticmethod
    async def page_delete(req, id: int):
        """Delete page."""
        if req.method != "POST":
            return RedirectResponse("/admin/pages")
        await PageRepository.delete(id)
        return RedirectResponse("/admin/pages?" + urlencode({"success": "Đã xóa trang"}), status_code=303)
    
    @staticmethod
    async def hero(req):
        """Admin hero."""
        from api.db import get_conn
        async with get_conn() as conn:
            if not conn:
                return AdminViews.layout(req, "Hero", P("Kết nối database để sửa Hero.", cls="text-amber-600"))
        
        r = await HeroRepository.get_for_edit()
        f = Form(method="post", action="/admin/hero/save", cls="space-y-4")(
            Div(Label("Promo (nhãn nhỏ)"), Input(name="promo", value=r["promo"] or "", cls="w-full border rounded px-2 py-1")),
            Div(Label("Tiêu đề"), Input(name="title", value=r["title"] or "", cls="w-full border rounded px-2 py-1")),
            Div(Label("Phụ đề"), Textarea(name="subtitle", cls="w-full border rounded px-2 py-1", rows=2)(r["subtitle"] or "")),
            Div(Label("Ảnh URL"), Input(name="image", value=r["image"] or "", cls="w-full border rounded px-2 py-1")),
            Div(Label("Nút (text)"), Input(name="button_text", value=r["button_text"] or "Shop Now", cls="w-full border rounded px-2 py-1")),
            Button("Lưu", type="submit", cls="px-3 py-1.5 bg-[#2F5233] text-white rounded hover:bg-[#1a331d] text-sm font-medium"),
        )
        return AdminViews.layout(req, "Hero", Div(H1("Hero Banner", cls="text-2xl font-bold mb-4"), f))
    
    @staticmethod
    async def hero_save(req):
        """Save hero."""
        if req.method != "POST":
            return RedirectResponse("/admin/hero")
        form = await req.form()
        await HeroRepository.update(
            promo=form.get("promo"),
            title=form.get("title"),
            subtitle=form.get("subtitle"),
            image=form.get("image"),
            button_text=form.get("button_text"),
        )
        return RedirectResponse("/admin/hero?" + urlencode({"success": "Đã lưu Hero"}), status_code=303)
    
    @staticmethod
    async def site(req):
        """Admin site config."""
        from api.db import get_conn
        async with get_conn() as conn:
            if not conn:
                return AdminViews.layout(req, "Site Config", P("Kết nối database để sửa cấu hình.", cls="text-amber-600"))
        
        brochures = await CategoryRepository.get_brochures_for_admin()
        config = await SiteConfigRepository.get_all()
        
        def _as_dict(v):
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
        
        brand = _as_dict(config.get("brand"))
        if not brand and _as_dict(config.get("header")):
            brand = {**_as_dict(config.get("header")), "icon": "fas fa-mountain"}
        if not brand.get("icon"):
            brand = {**brand, "icon": "fas fa-mountain"}
        topbar = _as_dict(config.get("topbar"))
        footer = _as_dict(config.get("footer"))
        
        forms = []
        forms.append(Div(cls="mb-8")(H2("Thương hiệu (dùng chung Header & Footer)", cls="text-lg font-bold mb-2"),
            P("Tên app và icon hiển thị ở nav và footer.", cls="text-gray-600 text-sm mb-2"),
            Form(method="post", action="/admin/site/brand", cls="space-y-2")(
                Div(Label("Tên app"), Input(name="siteName", value=brand.get("siteName", ""), cls="w-full border rounded px-2 py-1")),
                Div(Label("Tagline"), Input(name="tagline", value=brand.get("tagline", ""), cls="w-full border rounded px-2 py-1")),
                Div(Label("Icon (Font Awesome class, VD: fas fa-mountain)"), Input(name="icon", value=brand.get("icon", "fas fa-mountain"), cls="w-full border rounded px-2 py-1")),
                Button("Lưu Thương hiệu", type="submit", cls="px-3 py-1.5 bg-[#2F5233] text-white rounded hover:bg-[#1a331d] text-sm"),
            )))
        forms.append(Div(cls="mb-8")(H2("Topbar", cls="text-lg font-bold mb-2"),
            Form(method="post", action="/admin/site/topbar", cls="space-y-2")(
                Div(Label("Free shipping text"), Input(name="freeShipping", value=topbar.get("freeShipping", ""), cls="w-full border rounded px-2 py-1")),
                Div(Label("Hotline"), Input(name="hotline", value=topbar.get("hotline", ""), cls="w-full border rounded px-2 py-1")),
                Button("Lưu Topbar", type="submit", cls="px-3 py-1.5 bg-[#2F5233] text-white rounded hover:bg-[#1a331d] text-sm"),
            )))
        forms.append(Div(cls="mb-8")(H2("Footer", cls="text-lg font-bold mb-2"),
            Form(method="post", action="/admin/site/footer", cls="space-y-2")(
                Div(Label("Địa chỉ"), Input(name="address", value=footer.get("address", ""), cls="w-full border rounded px-2 py-1")),
                Div(Label("Điện thoại"), Input(name="phone", value=footer.get("phone", ""), cls="w-full border rounded px-2 py-1")),
                Div(Label("Email"), Input(name="email", value=footer.get("email", ""), cls="w-full border rounded px-2 py-1")),
                Div(Label("Mô tả công ty"), Input(name="description", value=footer.get("description", ""), cls="w-full border rounded px-2 py-1")),
                Div(Label("Copyright"), Input(name="copyright", value=footer.get("copyright", ""), cls="w-full border rounded px-2 py-1")),
                Button("Lưu Footer", type="submit", cls="px-3 py-1.5 bg-[#2F5233] text-white rounded hover:bg-[#1a331d] text-sm"),
            )))
        for b in brochures:
            forms.append(Div(cls="mb-4 p-3 border rounded")(H2(f"Brochure: {b['slug']}", cls="text-lg font-bold mb-2"),
                Form(method="post", action=f"/admin/site/brochure/{b['slug']}", cls="space-y-2")(
                    Div(Label("Tiêu đề"), Input(name="title", value=b["title"] or "", cls="w-full border rounded px-2 py-1")),
                    Div(Label("Mô tả"), Input(name="desc", value=b["desc"] or "", cls="w-full border rounded px-2 py-1")),
                    Div(Label("Ảnh URL"), Input(name="image", value=b["image"] or "", cls="w-full border rounded px-2 py-1")),
                    Div(Label("Nút"), Input(name="button_text", value=b["button_text"] or "", cls="w-full border rounded px-2 py-1")),
                    Button("Lưu", type="submit", cls="px-3 py-1.5 bg-[#2F5233] text-white rounded hover:bg-[#1a331d] text-sm font-medium"),
                )))
        return AdminViews.layout(req, "Site Config", Div(H1("Cấu hình site", cls="text-2xl font-bold mb-4"), *forms))
    
    @staticmethod
    async def site_brand(req):
        """Update brand config."""
        if req.method != "POST":
            return RedirectResponse("/admin/site")
        form = await req.form()
        await SiteConfigRepository.update_brand(
            site_name=form.get("siteName", ""),
            tagline=form.get("tagline", ""),
            icon=form.get("icon", "fas fa-mountain"),
        )
        return RedirectResponse("/admin/site", status_code=303)
    
    @staticmethod
    async def site_topbar(req):
        """Update topbar config."""
        if req.method != "POST":
            return RedirectResponse("/admin/site")
        form = await req.form()
        await SiteConfigRepository.update_topbar(
            free_shipping=form.get("freeShipping", ""),
            hotline=form.get("hotline", ""),
            support=form.get("support"),
        )
        return RedirectResponse("/admin/site", status_code=303)
    
    @staticmethod
    async def site_footer(req):
        """Update footer config."""
        if req.method != "POST":
            return RedirectResponse("/admin/site")
        form = await req.form()
        await SiteConfigRepository.update_footer(
            address=form.get("address", ""),
            phone=form.get("phone", ""),
            email=form.get("email", ""),
            description=form.get("description"),
            copyright=form.get("copyright"),
        )
        return RedirectResponse("/admin/site", status_code=303)
    
    @staticmethod
    async def site_brochure(req, slug: str):
        """Update brochure."""
        if req.method != "POST":
            return RedirectResponse("/admin/site")
        form = await req.form()
        await CategoryRepository.update_brochure(
            slug=slug,
            title=form.get("title"),
            desc=form.get("desc"),
            image=form.get("image"),
            button_text=form.get("button_text"),
        )
        return RedirectResponse("/admin/site", status_code=303)
