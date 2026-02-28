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
            (counts["products"], "fa-box", "Sản phẩm", "/admin/products", "bg-gradient-to-br from-blue-500 to-blue-600", "text-blue-600"),
            (counts["news"], "fa-newspaper", "Tin tức", "/admin/news", "bg-gradient-to-br from-purple-500 to-purple-600", "text-purple-600"),
            (counts["categories"], "fa-folder", "Danh mục", "/admin/categories", "bg-gradient-to-br from-green-500 to-green-600", "text-green-600"),
            (counts["pages"], "fa-file-alt", "Trang", "/admin/pages", "bg-gradient-to-br from-orange-500 to-orange-600", "text-orange-600"),
        ]
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
                    href="/admin/products",
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
                    href="/admin/pages",
                    cls="group flex items-center gap-3 p-3 rounded bg-white border-2 border-[#2F5233] text-[#2F5233] hover:bg-[#2F5233] hover:text-white hover:shadow-lg transition-all duration-300 transform hover:scale-105"
                )(
                    Div(cls="w-10 h-10 rounded bg-[#2F5233]/10 group-hover:bg-white/20 flex items-center justify-center")(
                        I(cls="fas fa-file-alt text-lg"),
                    ),
                    Div(
                        Span("Thêm trang", cls="font-semibold text-base block"),
                        Span("Tạo trang tĩnh", cls="text-gray-600 group-hover:text-white/80 text-sm block"),
                    ),
                ),
            ),
        )
        return AdminViews.layout(req, "Dashboard", Div(
            Div(cls="mb-5")(
                H1("Dashboard", cls="text-2xl font-bold text-gray-900 mb-2"),
                P("Chào mừng đến với CMS Mountain Harvest. Quản lý nội dung và cấu hình website của bạn.", cls="text-gray-600"),
            ),
            Div(cls="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mb-5")(*cards),
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
        add_form = Form(method="post", action="/admin/categories/add", cls="mb-4 p-4 bg-gradient-to-br from-gray-50 to-white border border-gray-200 rounded shadow-sm")(
            Div(cls="flex items-center gap-2 mb-4")(
                Div(cls="w-8 h-8 rounded bg-[#2F5233] flex items-center justify-center")(
                    I(cls="fas fa-plus text-white text-sm"),
                ),
                H2("Thêm danh mục mới", cls="text-lg font-bold text-gray-900"),
            ),
            Div(cls="grid grid-cols-1 md:grid-cols-12 gap-3 items-end")(
                Div(cls="md:col-span-8")(
                    Label("Tên danh mục", cls="block text-sm font-semibold mb-1.5 text-gray-700 flex items-center gap-2")(
                        Span("Tên"),
                        Span("*", cls="text-red-500"),
                    ),
                    Div(cls="relative")(
                        I(cls="fas fa-folder absolute left-2.5 top-1/2 transform -translate-y-1/2 text-gray-400 text-sm"),
                        Input(name="name", cls="w-full pl-9 pr-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-[#2F5233] focus:border-[#2F5233] transition", required=True, placeholder="Nhập tên danh mục"),
                    ),
                    P("Tên danh mục sẽ hiển thị trên website", cls="text-xs text-gray-500 mt-1"),
                ),
                Div(cls="md:col-span-3")(
                    Label("Thứ tự sắp xếp", cls="block text-sm font-semibold mb-1.5 text-gray-700")(
                        Span("Thứ tự"),
                    ),
                    Div(cls="relative")(
                        I(cls="fas fa-sort-numeric-down absolute left-2.5 top-1/2 transform -translate-y-1/2 text-gray-400 text-sm"),
                        Input(name="sort_order", type="number", value="0", cls="w-full pl-9 pr-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-[#2F5233] focus:border-[#2F5233] transition"),
                    ),
                ),
                Div(cls="md:col-span-1")(
                    Button(type="submit", cls="w-full px-3 py-2 bg-gradient-to-r from-[#E85D04] to-[#c75003] text-white rounded hover:shadow-md transition-all duration-200 font-semibold flex items-center justify-center gap-1.5")(
                        I(cls="fas fa-check text-sm"),
                        Span("Thêm", cls="hidden md:inline text-sm"),
                    ),
                ),
            ),
        )
        rows_html = []
        for idx, r in enumerate(rows):
            is_even = idx % 2 == 0
            rows_html.append(Tr(cls=f"hover:bg-blue-50/50 transition-colors duration-150 {'bg-gray-50/50' if is_even else 'bg-white'}")(
                Td(r["id"], cls="px-3 py-2 border-t border-gray-200 font-mono text-gray-500 text-sm"),
                Td(r["name"], cls="px-3 py-2 border-t border-gray-200 font-semibold text-gray-900"),
                Td(r.get("sort_order", 0), cls="px-3 py-2 border-t border-gray-200 text-gray-600 text-sm"),
                Td(cls="px-3 py-2 border-t border-gray-200 whitespace-nowrap")(
                    Div(cls="flex items-center gap-1.5")(
                        A(
                            href=f"/admin/categories/{r['id']}/edit",
                            cls="inline-flex items-center justify-center w-7 h-7 text-blue-600 hover:bg-blue-100 rounded transition-all duration-200 hover:scale-110",
                            title="Chỉnh sửa"
                        )(
                            I(cls="fas fa-edit text-xs"),
                        ),
                        Form(method="post", action=f"/admin/categories/{r['id']}/delete", cls="inline")(
                            Button(
                                type="submit",
                                cls="inline-flex items-center justify-center w-7 h-7 text-red-600 hover:bg-red-100 rounded transition-all duration-200 hover:scale-110",
                                title="Xóa",
                                **{"data-confirm": "Xóa danh mục này?"}
                            )(
                                I(cls="fas fa-trash text-xs"),
                            ),
                        ),
                    ),
                ),
            ))
        table = Table(cls="w-full border-collapse")(
            Thead(cls="bg-gradient-to-r from-[#2F5233] to-[#1a331d] sticky top-0 z-10")(
                Tr(
                    Th("ID", cls="px-3 py-2 text-left text-xs font-bold text-white uppercase tracking-wider"),
                    Th("Tên", cls="px-3 py-2 text-left text-xs font-bold text-white uppercase tracking-wider"),
                    Th("Thứ tự", cls="px-3 py-2 text-left text-xs font-bold text-white uppercase tracking-wider"),
                    Th("Thao tác", cls="px-3 py-2 text-left text-xs font-bold text-white uppercase tracking-wider"),
                ),
            ),
            Tbody(*rows_html),
        )
        table_wrapper = Div(cls="overflow-x-auto rounded border border-gray-200 shadow-sm bg-white")(table) if rows_html else Div(cls="text-center py-12 px-3 rounded border-2 border-dashed border-gray-300 bg-gray-50")(
            Div(cls="w-16 h-16 mx-auto mb-3 rounded bg-gray-100 flex items-center justify-center")(
                I(cls="fas fa-folder-open text-2xl text-gray-400"),
            ),
            H3("Chưa có danh mục nào", cls="text-base font-semibold text-gray-900 mb-1.5"),
            P("Bắt đầu bằng cách thêm danh mục đầu tiên của bạn ở form phía trên.", cls="text-gray-600 mb-4"),
        )
        return AdminViews.layout(req, "Categories", Div(
            Div(cls="mb-4")(
                H1("Quản lý danh mục", cls="text-2xl font-bold text-gray-900 mb-1.5"),
                P("Tạo và quản lý các danh mục sản phẩm", cls="text-gray-600 text-sm"),
            ),
            add_form,
            table_wrapper
        ))
    
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
            Div(
                Label("Tên danh mục", cls="block text-sm font-semibold mb-1.5 text-gray-700 flex items-center gap-2")(
                    Span("Tên"),
                    Span("*", cls="text-red-500"),
                ),
                Div(cls="relative")(
                    I(cls="fas fa-folder absolute left-2.5 top-1/2 transform -translate-y-1/2 text-gray-400 text-sm"),
                    Input(name="name", value=r["name"], cls="w-full pl-9 pr-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-[#2F5233] focus:border-[#2F5233] transition", required=True),
                ),
            ),
            Div(
                Label("Thứ tự sắp xếp", cls="block text-sm font-semibold mb-1.5 text-gray-700"),
                Div(cls="relative")(
                    I(cls="fas fa-sort-numeric-down absolute left-2.5 top-1/2 transform -translate-y-1/2 text-gray-400 text-sm"),
                    Input(name="sort_order", type="number", value=r.get("sort_order", 0), cls="w-full pl-9 pr-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-[#2F5233] focus:border-[#2F5233] transition"),
                ),
            ),
            Div(cls="flex gap-2 pt-3")(
                Button("Lưu thay đổi", type="submit", cls="px-3 py-2 bg-gradient-to-r from-[#2F5233] to-[#1a331d] text-white rounded hover:shadow-md transition-all duration-200 font-semibold flex items-center gap-1.5")(
                    I(cls="fas fa-save text-sm"),
                    Span("Lưu"),
                ),
                A("Hủy", href="/admin/categories", cls="px-3 py-2 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition font-semibold flex items-center gap-1.5"),
            ),
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
        
        filter_form = Form(method="get", action="/admin/products", cls="mb-4 p-4 bg-white border border-gray-200 rounded shadow-sm")(
            Div(cls="flex items-center gap-2 mb-3")(
                I(cls="fas fa-filter text-[#2F5233]"),
                H3("Bộ lọc tìm kiếm", cls="text-base font-semibold text-gray-900"),
            ),
            Div(cls="grid grid-cols-1 md:grid-cols-4 gap-3")(
                Div(cls="md:col-span-2")(
                    Label("Tìm kiếm sản phẩm", cls="block text-sm font-semibold mb-1.5 text-gray-700"),
                    Div(cls="relative")(
                        I(cls="fas fa-search absolute left-2.5 top-1/2 transform -translate-y-1/2 text-gray-400 text-sm"),
                        Input(name="q", value=search, placeholder="Nhập tên sản phẩm...", cls="w-full pl-9 pr-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-[#2F5233] focus:border-[#2F5233] transition"),
                    ),
                ),
                Div(
                    Label("Danh mục", cls="block text-sm font-semibold mb-1.5 text-gray-700"),
                    Div(cls="relative")(
                        I(cls="fas fa-folder absolute left-2.5 top-1/2 transform -translate-y-1/2 text-gray-400 pointer-events-none text-sm"),
                        Select(
                            *([Option("Tất cả danh mục", value="")] + [Option(c, value=c, selected=(c == category)) for c in categories]),
                            name="category", cls="w-full pl-9 pr-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-[#2F5233] focus:border-[#2F5233] appearance-none bg-white",
                        ),
                    ),
                ),
                Div(
                    Label("Sắp xếp", cls="block text-sm font-semibold mb-1.5 text-gray-700"),
                    Div(cls="relative")(
                        I(cls="fas fa-sort absolute left-2.5 top-1/2 transform -translate-y-1/2 text-gray-400 pointer-events-none text-sm"),
                        Select(
                            Option("Mới nhất", value="newest", selected=(sort == "newest")),
                            Option("Cũ nhất", value="oldest", selected=(sort == "oldest")),
                            Option("Giá thấp → cao", value="price_asc", selected=(sort == "price_asc")),
                            Option("Giá cao → thấp", value="price_desc", selected=(sort == "price_desc")),
                            Option("Tên A-Z", value="name", selected=(sort == "name")),
                            name="sort", cls="w-full pl-9 pr-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-[#2F5233] focus:border-[#2F5233] appearance-none bg-white",
                        ),
                    ),
                ),
            ),
            Input(name="per_page", type="hidden", value=str(per)),
            Div(cls="flex justify-end mt-3")(
                Button("Áp dụng bộ lọc", type="submit", cls="px-3 py-2 bg-gradient-to-r from-[#2F5233] to-[#1a331d] text-white rounded hover:shadow-md transition-all duration-200 font-semibold flex items-center gap-1.5")(
                    I(cls="fas fa-filter text-sm"),
                    Span("Lọc"),
                ),
            ),
        )
        
        category_options = [Option("-- Chọn danh mục --", value="")] + [Option(c, value=c) for c in categories]
        add_form = Form(method="post", action="/admin/products/new", cls="mb-4 p-4 bg-gradient-to-br from-gray-50 to-white border border-gray-200 rounded shadow-sm")(
            Div(cls="flex items-center gap-2 mb-4")(
                Div(cls="w-8 h-8 rounded bg-gradient-to-br from-[#E85D04] to-[#c75003] flex items-center justify-center")(
                    I(cls="fas fa-plus text-white text-sm"),
                ),
                H2("Thêm sản phẩm mới", cls="text-lg font-bold text-gray-900"),
            ),
            Div(cls="space-y-4")(
                Div(
                    H3("Thông tin cơ bản", cls="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2")(
                        I(cls="fas fa-info-circle text-[#2F5233]"),
                        Span("Thông tin cơ bản"),
                    ),
                    Div(cls="grid grid-cols-1 md:grid-cols-2 gap-3")(
                        Div(
                            Label("Tên sản phẩm", cls="block text-sm font-semibold mb-2 text-gray-700 flex items-center gap-2")(
                                Span("Tên"),
                                Span("*", cls="text-red-500"),
                            ),
                            Div(cls="relative")(
                                I(cls="fas fa-box absolute left-2.5 top-1/2 transform -translate-y-1/2 text-gray-400"),
                                Input(name="name", cls="w-full pl-9 pr-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-[#2F5233] focus:border-[#2F5233] transition", required=True, placeholder="Nhập tên sản phẩm"),
                            ),
                        ),
                        Div(
                            Label("Slug (URL)", cls="block text-sm font-semibold mb-2 text-gray-700"),
                            Div(cls="relative")(
                                I(cls="fas fa-link absolute left-2.5 top-1/2 transform -translate-y-1/2 text-gray-400"),
                                Input(name="slug", cls="w-full pl-9 pr-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-[#2F5233] focus:border-[#2F5233] transition", placeholder="ca-chua-cherry-huu-co"),
                            ),
                            P("Để trống sẽ tự động tạo từ tên", cls="text-xs text-gray-500 mt-1"),
                        ),
                        Div(
                            Label("Danh mục", cls="block text-sm font-semibold mb-2 text-gray-700 flex items-center gap-2")(
                                Span("Danh mục"),
                                Span("*", cls="text-red-500"),
                            ),
                            Div(cls="relative")(
                                I(cls="fas fa-folder absolute left-2.5 top-1/2 transform -translate-y-1/2 text-gray-400 pointer-events-none"),
                                Select(*category_options, name="category", cls="w-full pl-9 pr-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-[#2F5233] focus:border-[#2F5233] appearance-none bg-white", required=True),
                            ),
                        ),
                        Div(
                            Label("Đơn vị", cls="block text-sm font-semibold mb-2 text-gray-700"),
                            Div(cls="relative")(
                                I(cls="fas fa-weight absolute left-2.5 top-1/2 transform -translate-y-1/2 text-gray-400"),
                                Input(name="unit", cls="w-full pl-9 pr-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-[#2F5233] focus:border-[#2F5233] transition", placeholder="/500g"),
                            ),
                        ),
                    ),
                ),
                Div(
                    H3("Giá và khuyến mãi", cls="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2")(
                        I(cls="fas fa-tags text-[#E85D04]"),
                        Span("Giá và khuyến mãi"),
                    ),
                    Div(cls="grid grid-cols-1 md:grid-cols-3 gap-3")(
                        Div(
                            Label("Giá bán (VNĐ)", cls="block text-sm font-semibold mb-2 text-gray-700 flex items-center gap-2")(
                                Span("Giá"),
                                Span("*", cls="text-red-500"),
                            ),
                            Div(cls="relative")(
                                I(cls="fas fa-money-bill-wave absolute left-2.5 top-1/2 transform -translate-y-1/2 text-gray-400"),
                                Input(name="price", type="number", cls="w-full pl-9 pr-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-[#2F5233] focus:border-[#2F5233] transition", required=True, placeholder="0"),
                            ),
                        ),
                        Div(
                            Label("Giá gốc (VNĐ)", cls="block text-sm font-semibold mb-2 text-gray-700"),
                            Div(cls="relative")(
                                I(cls="fas fa-tag absolute left-2.5 top-1/2 transform -translate-y-1/2 text-gray-400"),
                                Input(name="original_price", type="number", cls="w-full pl-9 pr-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-[#2F5233] focus:border-[#2F5233] transition", placeholder="0"),
                            ),
                            P("Để trống nếu không có", cls="text-xs text-gray-500 mt-1"),
                        ),
                        Div(
                            Label("Giảm giá", cls="block text-sm font-semibold mb-2 text-gray-700"),
                            Div(cls="relative")(
                                I(cls="fas fa-percent absolute left-2.5 top-1/2 transform -translate-y-1/2 text-gray-400"),
                                Input(name="discount", cls="w-full pl-9 pr-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-[#2F5233] focus:border-[#2F5233] transition", placeholder="-15%"),
                            ),
                        ),
                    ),
                ),
                Div(
                    H3("Hình ảnh và mô tả", cls="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2")(
                        I(cls="fas fa-image text-purple-600"),
                        Span("Hình ảnh và mô tả"),
                    ),
                    Div(cls="space-y-4")(
                        Div(
                            Label("URL hình ảnh", cls="block text-sm font-semibold mb-2 text-gray-700"),
                            Div(cls="relative")(
                                I(cls="fas fa-image absolute left-2.5 top-1/2 transform -translate-y-1/2 text-gray-400"),
                                Input(name="image", type="url", cls="w-full pl-9 pr-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-[#2F5233] focus:border-[#2F5233] transition", placeholder="https://example.com/image.jpg"),
                            ),
                        ),
                        Div(
                            Label("Mô tả sản phẩm", cls="block text-sm font-semibold mb-2 text-gray-700"),
                            Textarea(name="description", cls="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-[#2F5233] focus:border-[#2F5233] transition", rows=4, placeholder="Nhập mô tả chi tiết về sản phẩm..."),
                        ),
                        Div(
                            Label("Tags", cls="block text-sm font-semibold mb-2 text-gray-700"),
                            Div(cls="relative")(
                                I(cls="fas fa-tags absolute left-2.5 top-1/2 transform -translate-y-1/2 text-gray-400"),
                                Input(name="tags", cls="w-full pl-9 pr-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-[#2F5233] focus:border-[#2F5233] transition", placeholder="Organic, Best Seller, Fresh"),
                            ),
                            P("Phân cách bằng dấu phẩy", cls="text-xs text-gray-500 mt-1"),
                        ),
                    ),
                ),
                Div(
                    H3("Cài đặt khác", cls="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2")(
                        I(cls="fas fa-cog text-gray-600"),
                        Span("Cài đặt khác"),
                    ),
                    Div(cls="grid grid-cols-2 md:grid-cols-4 gap-3")(
                        Div(cls="flex items-center gap-3 p-4 border border-gray-200 rounded hover:bg-gray-50 transition")(
                            Input(name="is_hot", type="checkbox", value="1", id="is_hot", cls="w-5 h-5 text-[#E85D04] border-gray-300 rounded focus:ring-[#E85D04]"),
                            Label("Sản phẩm hot", html_for="is_hot", cls="text-sm font-medium text-gray-700 cursor-pointer"),
                        ),
                        Div(
                            Label("Rating", cls="block text-sm font-semibold mb-2 text-gray-700"),
                            Input(name="rating", type="number", step="0.1", value="0", cls="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-[#2F5233] focus:border-[#2F5233] transition"),
                        ),
                        Div(
                            Label("Reviews", cls="block text-sm font-semibold mb-2 text-gray-700"),
                            Input(name="reviews", type="number", value="0", cls="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-[#2F5233] focus:border-[#2F5233] transition"),
                        ),
                        Div(
                            Label("Thứ tự", cls="block text-sm font-semibold mb-2 text-gray-700"),
                            Input(name="sort_order", type="number", value="0", cls="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-[#2F5233] focus:border-[#2F5233] transition"),
                        ),
                    ),
                ),
                Div(cls="border-t border-gray-200 pt-6")(
                    Div(cls="flex items-center justify-between mb-4 cursor-pointer", id="seo-toggle", onclick="document.getElementById('seo-section').classList.toggle('hidden')")(
                        H3("SEO Settings", cls="text-lg font-semibold text-gray-900 flex items-center gap-2")(
                            I(cls="fas fa-search text-blue-600"),
                            Span("SEO Settings"),
                        ),
                        I(cls="fas fa-chevron-down text-gray-400 transition-transform", id="seo-chevron"),
                    ),
                    Div(id="seo-section", cls="space-y-4")(
                        Div(
                            Label("Meta Title", cls="block text-sm font-semibold mb-2 text-gray-700"),
                            Input(name="meta_title", placeholder="SEO title (tối đa 60 ký tự)", cls="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"),
                            P("Tiêu đề hiển thị trên kết quả tìm kiếm", cls="text-xs text-gray-500 mt-1"),
                        ),
                        Div(
                            Label("Meta Description", cls="block text-sm font-semibold mb-2 text-gray-700"),
                            Textarea(name="meta_description", placeholder="SEO description (tối đa 160 ký tự)", cls="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition", rows=2),
                        ),
                        Div(cls="grid grid-cols-1 md:grid-cols-3 gap-3")(
                            Div(
                                Label("H1 Custom", cls="block text-sm font-semibold mb-2 text-gray-700"),
                                Input(name="h1_custom", placeholder="H1", cls="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"),
                            ),
                            Div(
                                Label("H2 Custom", cls="block text-sm font-semibold mb-2 text-gray-700"),
                                Input(name="h2_custom", placeholder="H2", cls="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"),
                            ),
                            Div(
                                Label("H3 Custom", cls="block text-sm font-semibold mb-2 text-gray-700"),
                                Input(name="h3_custom", placeholder="H3", cls="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"),
                            ),
                        ),
                    ),
                ),
            ),
            Div(cls="flex gap-3 pt-6 border-t border-gray-200")(
                Button("Thêm sản phẩm", type="submit", cls="px-3 py-2 bg-gradient-to-r from-[#E85D04] to-[#c75003] text-white rounded hover:shadow-lg transition-all duration-200 font-semibold flex items-center gap-2")(
                    I(cls="fas fa-check"),
                    Span("Thêm"),
                ),
                A("Hủy", href="/admin/products", cls="px-3 py-2 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition font-semibold flex items-center gap-2"),
            ),
        )
        
        rows_html = []
        for idx, r in enumerate(rows):
            is_even = idx % 2 == 0
            rows_html.append(Tr(cls=f"hover:bg-blue-50/50 transition-colors duration-150 {'bg-gray-50/50' if is_even else 'bg-white'}")(
                Td(r["id"], cls="px-3 py-2 border-t border-gray-200 font-mono text-gray-500 text-sm"),
                Td(
                    Div(cls="font-semibold text-gray-900")(r["name"]),
                    cls="px-3 py-2 border-t border-gray-200"
                ),
                Td(
                    Span(r["category"], cls="inline-flex items-center px-2.5 py-1 rounded text-xs font-medium bg-green-100 text-green-800"),
                    cls="px-3 py-2 border-t border-gray-200"
                ),
                Td(
                    Span(f"{r['price']:,}đ", cls="font-semibold text-gray-900"),
                    cls="px-3 py-2 border-t border-gray-200"
                ),
                Td(
                    Img(src=r["image"] or "", cls="w-12 h-12 object-cover rounded border-2 border-gray-200 shadow-sm") if r["image"] else Div(cls="w-12 h-12 rounded bg-gray-100 flex items-center justify-center")(
                        I(cls="fas fa-image text-gray-400 text-sm")
                    ),
                    cls="px-3 py-2 border-t border-gray-200"
                ),
                Td(cls="px-3 py-2 border-t border-gray-200 whitespace-nowrap")(
                    Div(cls="flex items-center gap-2")(
                        A(
                            href=f"/admin/products/{r['id']}/edit",
                            cls="inline-flex items-center justify-center w-8 h-8 text-blue-600 hover:bg-blue-100 rounded transition-all duration-200 hover:scale-110",
                            title="Chỉnh sửa"
                        )(
                            I(cls="fas fa-edit text-sm"),
                        ),
                        Form(method="post", action=f"/admin/products/{r['id']}/delete", cls="inline")(
                            Button(
                                type="submit",
                                cls="inline-flex items-center justify-center w-8 h-8 text-red-600 hover:bg-red-100 rounded transition-all duration-200 hover:scale-110",
                                title="Xóa",
                                **{"data-confirm": "Xóa sản phẩm này?"}
                            )(
                                I(cls="fas fa-trash text-sm"),
                            ),
                        ),
                    ),
                ),
            ))
        table = Table(cls="w-full border-collapse")(
            Thead(cls="bg-gradient-to-r from-[#2F5233] to-[#1a331d] sticky top-0 z-10")(
                Tr(
                    Th("ID", cls="px-3 py-2 text-left text-xs font-bold text-white uppercase tracking-wider"),
                    Th("Tên", cls="px-3 py-2 text-left text-xs font-bold text-white uppercase tracking-wider"),
                    Th("Danh mục", cls="px-3 py-2 text-left text-xs font-bold text-white uppercase tracking-wider"),
                    Th("Giá", cls="px-3 py-2 text-left text-xs font-bold text-white uppercase tracking-wider"),
                    Th("Ảnh", cls="px-3 py-2 text-left text-xs font-bold text-white uppercase tracking-wider"),
                    Th("Thao tác", cls="px-3 py-2 text-left text-xs font-bold text-white uppercase tracking-wider"),
                ),
            ),
            Tbody(*rows_html),
        )
        
        pagination = []
        if total_pages > 1:
            # Show first page, last page, current page, and pages around current
            pages_to_show = []
            if total_pages <= 7:
                pages_to_show = list(range(1, total_pages + 1))
            else:
                pages_to_show = [1]
                if page > 3:
                    pages_to_show.append("...")
                start = max(2, page - 1)
                end = min(total_pages - 1, page + 1)
                for p in range(start, end + 1):
                    pages_to_show.append(p)
                if page < total_pages - 2:
                    pages_to_show.append("...")
                pages_to_show.append(total_pages)
            
            for p in pages_to_show:
                if p == "...":
                    pagination.append(Span("...", cls="px-2 text-gray-500"))
                else:
                    qs = AdminController._build_query_string(base_params, {"page": str(p)})
                    if p == page:
                        pagination.append(Span(str(p), cls="inline-flex items-center justify-center w-10 h-10 bg-gradient-to-r from-[#2F5233] to-[#1a331d] text-white rounded font-semibold text-sm shadow-sm"))
                    else:
                        pagination.append(A(str(p), href=f"/admin/products{qs}", cls="inline-flex items-center justify-center w-10 h-10 border border-gray-300 rounded hover:bg-gray-100 hover:border-[#2F5233] text-gray-700 text-sm font-medium transition"))
            pagination_html = Nav(cls="flex items-center justify-center gap-2 mt-4")(
                A(
                    I(cls="fas fa-chevron-left"),
                    href=f"/admin/products{AdminController._build_query_string(base_params, {'page': str(max(1, page - 1))})}",
                    cls="inline-flex items-center justify-center w-10 h-10 border border-gray-300 rounded hover:bg-gray-100 text-gray-700 transition" + (" opacity-50 pointer-events-none cursor-not-allowed" if page <= 1 else ""),
                    title="Trang trước"
                ),
                *pagination,
                A(
                    I(cls="fas fa-chevron-right"),
                    href=f"/admin/products{AdminController._build_query_string(base_params, {'page': str(min(total_pages, page + 1))})}",
                    cls="inline-flex items-center justify-center w-10 h-10 border border-gray-300 rounded hover:bg-gray-100 text-gray-700 transition" + (" opacity-50 pointer-events-none cursor-not-allowed" if page >= total_pages else ""),
                    title="Trang sau"
                ),
            )
        else:
            pagination_html = Div()
        
        table_wrapper = Div(cls="overflow-x-auto rounded border border-gray-200 shadow-sm bg-white")(table) if rows_html else Div(cls="text-center py-12 px-3 rounded border-2 border-dashed border-gray-300 bg-gray-50")(
            Div(cls="w-16 h-16 mx-auto mb-4 rounded bg-gradient-to-br from-blue-100 to-purple-100 flex items-center justify-center")(
                I(cls="fas fa-box-open text-4xl text-blue-500"),
            ),
            H3("Chưa có sản phẩm nào", cls="text-xl font-bold text-gray-900 mb-2"),
            P("Bắt đầu bằng cách thêm sản phẩm đầu tiên của bạn.", cls="text-gray-600 mb-4"),
            A(
                "Thêm sản phẩm đầu tiên",
                href="#add-form",
                cls="inline-flex items-center gap-2 px-3 py-2 bg-gradient-to-r from-[#E85D04] to-[#c75003] text-white rounded hover:shadow-lg transition font-semibold"
            )(
                I(cls="fas fa-plus"),
                Span("Thêm sản phẩm"),
            ),
        )
        
        header = Div(cls="flex flex-wrap justify-between items-center gap-3 mb-4")(
            Div(
                H1("Quản lý sản phẩm", cls="text-2xl font-bold text-gray-900 mb-1.5"),
                Div(cls="flex items-center gap-3 text-sm text-gray-600")(
                    Span(f"{total} sản phẩm", cls="flex items-center gap-1")(
                        I(cls="fas fa-box"),
                        Span(f"{total}"),
                    ),
                    Span(f"Trang {page}/{total_pages}", cls="flex items-center gap-1") if total_pages > 1 else None,
                ),
            ),
            A(
                "Thêm sản phẩm",
                href="#add-form",
                cls="px-3 py-2 bg-gradient-to-r from-[#E85D04] to-[#c75003] text-white rounded hover:shadow-lg transition font-semibold flex items-center gap-2"
            )(
                I(cls="fas fa-plus"),
                Span("Thêm mới"),
            ),
        )
        return AdminViews.layout(req, "Products", Div(header, filter_form, Div(id="add-form")(add_form), table_wrapper, pagination_html))
    
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
            Div(cls="flex flex-wrap gap-3 items-center")(
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
        
        filter_form = Form(method="get", action="/admin/news", cls="mb-4 p-3 bg-white border border-gray-200 rounded shadow-sm")(
            Div(cls="flex items-center gap-2 mb-4")(
                I(cls="fas fa-filter text-[#2F5233]"),
                H3("Bộ lọc tìm kiếm", cls="text-lg font-semibold text-gray-900"),
            ),
            Div(cls="flex gap-3")(
                Div(cls="flex-1")(
                    Label("Tìm kiếm tin tức", cls="block text-sm font-semibold mb-2 text-gray-700"),
                    Div(cls="relative")(
                        I(cls="fas fa-search absolute left-2.5 top-1/2 transform -translate-y-1/2 text-gray-400"),
                        Input(name="q", value=search, placeholder="Tiêu đề, nội dung hoặc tác giả...", cls="w-full pl-9 pr-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-[#2F5233] focus:border-[#2F5233] transition"),
                    ),
                ),
                Div(cls="flex items-end")(
                    Button("Áp dụng bộ lọc", type="submit", cls="px-3 py-2 bg-gradient-to-r from-[#2F5233] to-[#1a331d] text-white rounded hover:shadow-lg transition-all duration-200 font-semibold flex items-center gap-2")(
                        I(cls="fas fa-filter"),
                        Span("Lọc"),
                    ),
                ),
            ),
            Input(name="per_page", type="hidden", value=str(per)),
        )
        
        rows_html = []
        for idx, r in enumerate(rows):
            is_even = idx % 2 == 0
            rows_html.append(Tr(cls=f"hover:bg-blue-50/50 transition-colors duration-150 {'bg-gray-50/50' if is_even else 'bg-white'}")(
                Td(r["id"], cls="px-3 py-2 border-t border-gray-200 font-mono text-gray-500 text-sm"),
                Td(
                    Div(cls="font-semibold text-gray-900")(r["title"]),
                    cls="px-3 py-2 border-t border-gray-200"
                ),
                Td(r["date"] or "-", cls="px-3 py-2 border-t border-gray-200 text-gray-600 text-sm"),
                Td(r["author"] or "-", cls="px-3 py-2 border-t border-gray-200 text-gray-600 text-sm"),
                Td(
                    Img(src=r["image"] or "", cls="w-12 h-12 object-cover rounded border-2 border-gray-200 shadow-sm") if r.get("image") else Div(cls="w-12 h-12 rounded bg-gray-100 flex items-center justify-center")(
                        I(cls="fas fa-image text-gray-400 text-sm")
                    ),
                    cls="px-3 py-2 border-t border-gray-200"
                ),
                Td(cls="px-3 py-2 border-t border-gray-200 whitespace-nowrap")(
                    Div(cls="flex items-center gap-2")(
                        A(
                            href=f"/admin/news/{r['id']}/edit",
                            cls="inline-flex items-center justify-center w-8 h-8 text-blue-600 hover:bg-blue-100 rounded transition-all duration-200 hover:scale-110",
                            title="Chỉnh sửa"
                        )(
                            I(cls="fas fa-edit text-sm"),
                        ),
                        Form(method="post", action=f"/admin/news/{r['id']}/delete", cls="inline")(
                            Button(
                                type="submit",
                                cls="inline-flex items-center justify-center w-8 h-8 text-red-600 hover:bg-red-100 rounded transition-all duration-200 hover:scale-110",
                                title="Xóa",
                                **{"data-confirm": "Xóa tin này?"}
                            )(
                                I(cls="fas fa-trash text-sm"),
                            ),
                        ),
                    ),
                ),
            ))
        table = Table(cls="w-full border-collapse")(
            Thead(cls="bg-gradient-to-r from-[#2F5233] to-[#1a331d] sticky top-0 z-10")(
                Tr(
                    Th("ID", cls="px-3 py-2 text-left text-xs font-bold text-white uppercase tracking-wider"),
                    Th("Tiêu đề", cls="px-3 py-2 text-left text-xs font-bold text-white uppercase tracking-wider"),
                    Th("Ngày", cls="px-3 py-2 text-left text-xs font-bold text-white uppercase tracking-wider"),
                    Th("Tác giả", cls="px-3 py-2 text-left text-xs font-bold text-white uppercase tracking-wider"),
                    Th("Ảnh", cls="px-3 py-2 text-left text-xs font-bold text-white uppercase tracking-wider"),
                    Th("Thao tác", cls="px-3 py-2 text-left text-xs font-bold text-white uppercase tracking-wider"),
                ),
            ),
            Tbody(*rows_html),
        )
        
        pagination = []
        if total_pages > 1:
            pages_to_show = []
            if total_pages <= 7:
                pages_to_show = list(range(1, total_pages + 1))
            else:
                pages_to_show = [1]
                if page > 3:
                    pages_to_show.append("...")
                start = max(2, page - 1)
                end = min(total_pages - 1, page + 1)
                for p in range(start, end + 1):
                    pages_to_show.append(p)
                if page < total_pages - 2:
                    pages_to_show.append("...")
                pages_to_show.append(total_pages)
            
            for p in pages_to_show:
                if p == "...":
                    pagination.append(Span("...", cls="px-2 text-gray-500"))
                else:
                    qs = AdminController._build_query_string(base_params, {"page": str(p)})
                    if p == page:
                        pagination.append(Span(str(p), cls="inline-flex items-center justify-center w-10 h-10 bg-gradient-to-r from-[#2F5233] to-[#1a331d] text-white rounded font-semibold text-sm shadow-sm"))
                    else:
                        pagination.append(A(str(p), href=f"/admin/news{qs}", cls="inline-flex items-center justify-center w-10 h-10 border border-gray-300 rounded hover:bg-gray-100 hover:border-[#2F5233] text-gray-700 text-sm font-medium transition"))
            pagination_html = Nav(cls="flex items-center justify-center gap-2 mt-4")(
                A(
                    I(cls="fas fa-chevron-left"),
                    href=f"/admin/news{AdminController._build_query_string(base_params, {'page': str(max(1, page - 1))})}",
                    cls="inline-flex items-center justify-center w-10 h-10 border border-gray-300 rounded hover:bg-gray-100 text-gray-700 transition" + (" opacity-50 pointer-events-none cursor-not-allowed" if page <= 1 else ""),
                    title="Trang trước"
                ),
                *pagination,
                A(
                    I(cls="fas fa-chevron-right"),
                    href=f"/admin/news{AdminController._build_query_string(base_params, {'page': str(min(total_pages, page + 1))})}",
                    cls="inline-flex items-center justify-center w-10 h-10 border border-gray-300 rounded hover:bg-gray-100 text-gray-700 transition" + (" opacity-50 pointer-events-none cursor-not-allowed" if page >= total_pages else ""),
                    title="Trang sau"
                ),
            )
        else:
            pagination_html = Div()
        
        table_wrapper = Div(cls="overflow-x-auto rounded border border-gray-200 shadow-sm bg-white")(table) if rows_html else Div(cls="text-center py-12 px-3 rounded border-2 border-dashed border-gray-300 bg-gray-50")(
            Div(cls="w-16 h-16 mx-auto mb-4 rounded bg-gradient-to-br from-purple-100 to-pink-100 flex items-center justify-center")(
                I(cls="fas fa-newspaper text-4xl text-purple-500"),
            ),
            H3("Chưa có tin tức nào", cls="text-xl font-bold text-gray-900 mb-2"),
            P("Bắt đầu bằng cách thêm tin tức đầu tiên của bạn.", cls="text-gray-600 mb-4"),
            A(
                "Thêm tin tức đầu tiên",
                href="/admin/news/add",
                cls="inline-flex items-center gap-2 px-3 py-2 bg-gradient-to-r from-[#E85D04] to-[#c75003] text-white rounded hover:shadow-lg transition font-semibold"
            )(
                I(cls="fas fa-plus"),
                Span("Thêm tin tức"),
            ),
        )
        
        header = Div(cls="flex flex-wrap justify-between items-center gap-3 mb-4")(
            Div(
                H1("Quản lý tin tức", cls="text-2xl font-bold text-gray-900 mb-1.5"),
                Div(cls="flex items-center gap-3 text-sm text-gray-600")(
                    Span(f"{total} tin", cls="flex items-center gap-1")(
                        I(cls="fas fa-newspaper"),
                        Span(f"{total}"),
                    ),
                    Span(f"Trang {page}/{total_pages}", cls="flex items-center gap-1") if total_pages > 1 else None,
                ),
            ),
            A(
                "Thêm tin mới",
                href="/admin/news/add",
                cls="px-3 py-2 bg-gradient-to-r from-[#E85D04] to-[#c75003] text-white rounded hover:shadow-lg transition font-semibold flex items-center gap-2"
            )(
                I(cls="fas fa-plus"),
                Span("Thêm mới"),
            ),
        )
        return AdminViews.layout(req, "News", Div(header, filter_form, table_wrapper, pagination_html))
    
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
                Button("Lưu", type="submit", cls="px-3 py-1.5 bg-blue-600 text-white rounded hover:bg-blue-700 font-medium text-sm"),
                A("Hủy", href="/admin/news", cls="px-3 py-1.5 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 font-medium text-sm"),
            ),
        )
        return AdminViews.layout(req, "Thêm tin mới", Div(H1("Thêm tin mới", cls="text-2xl font-bold mb-4 text-gray-800"), form), include_editor=True)
    
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
            Div(cls="grid grid-cols-2 gap-3")(
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
            Div(cls="grid grid-cols-3 gap-3")(
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
                Button("Lưu", type="submit", cls="px-3 py-1.5 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm font-medium"),
                A("Hủy", href="/admin/news", cls="px-3 py-1.5 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 text-sm font-medium"),
            ),
        )
        return AdminViews.layout(req, "Sửa tin", Div(H1("Sửa tin", cls="text-2xl font-bold mb-4 text-gray-800"), f), include_editor=True)
    
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
            Div(cls="grid grid-cols-2 gap-3")(
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
        forms.append(Div(cls="mb-5")(H2("Thương hiệu (dùng chung Header & Footer)", cls="text-lg font-bold mb-2"),
            P("Tên app và icon hiển thị ở nav và footer.", cls="text-gray-600 text-sm mb-2"),
            Form(method="post", action="/admin/site/brand", cls="space-y-2")(
                Div(Label("Tên app"), Input(name="siteName", value=brand.get("siteName", ""), cls="w-full border rounded px-2 py-1")),
                Div(Label("Tagline"), Input(name="tagline", value=brand.get("tagline", ""), cls="w-full border rounded px-2 py-1")),
                Div(Label("Icon (Font Awesome class, VD: fas fa-mountain)"), Input(name="icon", value=brand.get("icon", "fas fa-mountain"), cls="w-full border rounded px-2 py-1")),
                Button("Lưu Thương hiệu", type="submit", cls="px-3 py-1.5 bg-[#2F5233] text-white rounded hover:bg-[#1a331d] text-sm"),
            )))
        forms.append(Div(cls="mb-5")(H2("Topbar", cls="text-lg font-bold mb-2"),
            Form(method="post", action="/admin/site/topbar", cls="space-y-2")(
                Div(Label("Free shipping text"), Input(name="freeShipping", value=topbar.get("freeShipping", ""), cls="w-full border rounded px-2 py-1")),
                Div(Label("Hotline"), Input(name="hotline", value=topbar.get("hotline", ""), cls="w-full border rounded px-2 py-1")),
                Button("Lưu Topbar", type="submit", cls="px-3 py-1.5 bg-[#2F5233] text-white rounded hover:bg-[#1a331d] text-sm"),
            )))
        forms.append(Div(cls="mb-5")(H2("Footer", cls="text-lg font-bold mb-2"),
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
