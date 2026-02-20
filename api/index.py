"""FastHTML CMS Backend for Mountain Harvest."""
import os
import base64
import json
from pathlib import Path
from starlette.responses import JSONResponse, FileResponse, RedirectResponse
from starlette.staticfiles import StaticFiles
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from fasthtml.common import *

from api.db import get_conn, init_db

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PUBLIC_DIR = PROJECT_ROOT / "public"
STATIC_PATH = str(PUBLIC_DIR)


def basic_auth(req) -> bool:
    user = os.getenv("ADMIN_USER")
    pwd = os.getenv("ADMIN_PASSWORD")
    if not user or not pwd:
        return True
    auth = req.headers.get("Authorization")
    if not auth or not auth.startswith("Basic "):
        return False
    try:
        decoded = base64.b64decode(auth[6:]).decode()
        u, p = decoded.split(":", 1)
        return u == user and p == pwd
    except Exception:
        return False


def admin_before(req, auth=None):
    if not req.url.path.startswith("/admin"):
        return None
    if basic_auth(req):
        return None
    from starlette.responses import Response
    return Response(
        "Unauthorized",
        status_code=401,
        headers={"WWW-Authenticate": 'Basic realm="Admin"'},
    )


admin_beforeware = Beforeware(admin_before)

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


@rt("/")
async def index():
    """Serve frontend index.html."""
    idx = PUBLIC_DIR / "index.html"
    if idx.exists():
        return FileResponse(idx)
    return Div("Mountain Harvest - Add public/index.html")


# --- API: Products ---
def _apply_product_filters(items: list, category: str, price: str, standard: str) -> list:
    out = items
    if category:
        out = [x for x in out if x.get("category") == category]
    if price == "under50":
        out = [x for x in out if (x.get("price") or 0) < 50000]
    elif price == "50-200":
        out = [x for x in out if 50000 <= (x.get("price") or 0) <= 200000]
    elif price == "over200":
        out = [x for x in out if (x.get("price") or 0) > 200000]
    if standard:
        tag = standard  # Organic, VietGAP, Handmade
        out = [x for x in out if tag in (x.get("tags") or [])]
    return out


def _sort_products(items: list, sort: str) -> list:
    key = (sort or "newest").lower()
    if key == "bestseller":
        return sorted(items, key=lambda x: (x.get("reviews") or 0), reverse=True)
    if key == "price_asc":
        return sorted(items, key=lambda x: (x.get("price") or 0))
    if key == "price_desc":
        return sorted(items, key=lambda x: (x.get("price") or 0), reverse=True)
    return sorted(items, key=lambda x: x.get("id", 0), reverse=True)


@rt("/api/products")
async def api_products(
    category: str = None,
    price: str = None,
    standard: str = None,
    sort: str = "newest",
    page: int = 1,
    limit: int = 8,
):
    page = max(1, page)
    limit = max(1, min(100, limit))
    async with get_conn() as conn:
        if not conn:
            all_items = _mock_products()
            all_items = _apply_product_filters(all_items, category, price, standard)
            total = len(all_items)
            all_items = _sort_products(all_items, sort)
            start = (page - 1) * limit
            items = all_items[start : start + limit]
            total_pages = max(1, (total + limit - 1) // limit)
            return JSONResponse({
                "items": items, "total": total, "page": page, "limit": limit, "totalPages": total_pages,
            })
        base = "SELECT id, name, category, price, original_price, unit, image, rating, reviews, is_hot, discount, tags, description FROM products"
        where, params = [], []
        if category:
            where.append("category = $" + str(len(params) + 1))
            params.append(category)
        if price == "under50":
            where.append("price < 50000")
        elif price == "50-200":
            where.append("price >= 50000 AND price <= 200000")
        elif price == "over200":
            where.append("price > 200000")
        if standard:
            where.append("tags @> $" + str(len(params) + 1) + "::jsonb")
            params.append(json.dumps([standard]))
        where_sql = " AND ".join(where) if where else "1=1"
        order_map = {
            "newest": "ORDER BY id DESC",
            "bestseller": "ORDER BY reviews DESC NULLS LAST, id DESC",
            "price_asc": "ORDER BY price ASC, id DESC",
            "price_desc": "ORDER BY price DESC, id DESC",
        }
        order_sql = order_map.get((sort or "newest").lower(), order_map["newest"])
        count_row = await conn.fetchrow(f"SELECT COUNT(*) as n FROM products WHERE {where_sql}", *params)
        total = count_row["n"] or 0
        offset = (page - 1) * limit
        params.extend([limit, offset])
        rows = await conn.fetch(
            f"{base} WHERE {where_sql} {order_sql} LIMIT ${len(params)-1} OFFSET ${len(params)}",
            *params,
        )
    out = []
    for r in rows:
        out.append({
            "id": r["id"], "name": r["name"], "category": r["category"],
            "price": r["price"], "originalPrice": r["original_price"],
            "unit": r["unit"], "image": r["image"], "rating": float(r["rating"] or 0),
            "reviews": r["reviews"] or 0, "isHot": r["is_hot"],
            "discount": r["discount"], "tags": r["tags"] or [],
            "description": r["description"] or "",
        })
    total_pages = max(1, (total + limit - 1) // limit)
    return JSONResponse({"items": out, "total": total, "page": page, "limit": limit, "totalPages": total_pages})


@rt("/api/products/{id:int}")
async def api_product_detail(id: int):
    async with get_conn() as conn:
        if not conn:
            p = next((x for x in _mock_products() if x["id"] == id), None)
            return JSONResponse(p) if p else JSONResponse({"error": "Not found"}, status_code=404)
        r = await conn.fetchrow(
            "SELECT id, name, category, price, original_price, unit, image, rating, reviews, is_hot, discount, tags, description FROM products WHERE id = $1",
            id,
        )
    if not r:
        return JSONResponse({"error": "Not found"}, status_code=404)
    return JSONResponse({
        "id": r["id"], "name": r["name"], "category": r["category"],
        "price": r["price"], "originalPrice": r["original_price"],
        "unit": r["unit"], "image": r["image"], "rating": float(r["rating"] or 0),
        "reviews": r["reviews"] or 0, "isHot": r["is_hot"],
        "discount": r["discount"], "tags": r["tags"] or [],
        "description": r["description"] or "",
    })


# --- API: News ---
@rt("/api/news")
async def api_news(page: int = 1, limit: int = 6):
    page = max(1, page)
    limit = max(1, min(100, limit))
    async with get_conn() as conn:
        if not conn:
            all_items = _mock_news()
            total = len(all_items)
            start = (page - 1) * limit
            items = all_items[start : start + limit]
            return JSONResponse({"items": items, "total": total, "page": page, "limit": limit})
        count_row = await conn.fetchrow("SELECT COUNT(*) as n FROM news")
        total = count_row["n"] or 0
        offset = (page - 1) * limit
        rows = await conn.fetch(
            "SELECT id, title, image, summary, date FROM news ORDER BY sort_order, id LIMIT $1 OFFSET $2",
            limit, offset,
        )
    items = [dict(r) for r in rows]
    total_pages = max(1, (total + limit - 1) // limit)
    return JSONResponse({"items": items, "total": total, "page": page, "limit": limit, "totalPages": total_pages})


# --- API: Site (hero, categories, brochures, footer, topbar) ---
@rt("/api/site")
async def api_site():
    async with get_conn() as conn:
        if not conn:
            return JSONResponse(_mock_site())
        hero_row = await conn.fetchrow("SELECT promo, title, subtitle, image, button_text FROM hero LIMIT 1")
        brochures = await conn.fetch(
            "SELECT slug, title, desc, image, button_text FROM category_brochures ORDER BY id"
        )
        config_rows = await conn.fetch("SELECT key, value FROM site_config")
        cats = await conn.fetch("SELECT name FROM categories ORDER BY sort_order, id")
    hero = dict(hero_row) if hero_row else {}
    config = {r["key"]: r["value"] for r in config_rows}
    return JSONResponse({
        "hero": {
            "promo": hero.get("promo", "Summer Sale"),
            "title": hero.get("title", "Fresh Produce For Green Living"),
            "subtitle": hero.get("subtitle", "Up to 20% off on vegetables and fruits this week."),
            "image": hero.get("image", ""),
            "buttonText": hero.get("button_text", "Shop Now"),
        },
        "categories": [r["name"] for r in cats],
        "brochures": [
            {"slug": r["slug"], "title": r["title"], "desc": r["desc"], "image": r["image"], "buttonText": r["button_text"]}
            for r in brochures
        ],
        "topbar": config.get("topbar", {}),
        "footer": config.get("footer", {}),
    })


def _mock_products():
    return [
        {"id": 1, "name": "Cà Chua Cherry Hữu Cơ", "category": "Rau củ quả", "price": 45000, "originalPrice": 55000,
         "unit": None, "image": "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?ixlib=rb-1.2.1&auto=format&fit=crop&w=600&q=80",
         "rating": 4.5, "reviews": 45, "isHot": False, "discount": "-15%", "tags": ["Organic"], "description": "Cà chua cherry hữu cơ."},
        {"id": 2, "name": "Gạo Lứt Đỏ Huyết Rồng", "category": "Thực phẩm khô", "price": 80000, "originalPrice": None,
         "unit": "/2kg", "image": "https://images.unsplash.com/photo-1586201375761-83865001e31c?ixlib=rb-1.2.1&auto=format&fit=crop&w=600&q=80",
         "rating": 5, "reviews": 128, "isHot": False, "discount": None, "tags": [], "description": "Gạo lứt đỏ huyết rồng."},
    ]


def _mock_news():
    return [
        {"id": 1, "title": "Mùa Thu Hoạch Bơ Sáp 034", "image": "https://images.unsplash.com/photo-1523049673856-35691f096315?ixlib=rb-1.2.1&auto=format&fit=crop&w=600&q=80",
         "summary": "Những trái bơ sáp 034 đầu tiên đã lên kệ.", "date": "03/02/2026"},
    ]


def _mock_site():
    return {
        "hero": {"promo": "Summer Sale", "title": "Fresh Produce For Green Living", "subtitle": "Up to 20% off.",
                 "image": "https://images.unsplash.com/photo-1542838132-92c53300491e?w=1920&q=80", "buttonText": "Shop Now"},
        "categories": ["Rau củ quả", "Hạt & Ngũ cốc", "Gia dụng"],
        "brochures": [
            {"slug": "fresh", "title": "Fresh Produce", "desc": "Harvested from Da Lat farms.", "image": "", "buttonText": "Shop Now"},
            {"slug": "essentials", "title": "Green Essentials", "desc": "Natural home care products.", "image": "", "buttonText": "Explore"},
        ],
        "topbar": {"freeShipping": "Free shipping for orders over 500k", "hotline": "1900 1234", "support": "Customer Support"},
        "footer": {"address": "123 Đường Mây Núi, Đà Lạt", "phone": "1900 1234", "email": "cskh@mountainharvest.vn"},
    }


# --- Startup: init DB ---
@app.on_event("startup")
async def startup():
    await init_db()


# --- Admin Layout ---
NAV_ITEMS = [
    ("/admin", "fa-gauge-high", "Dashboard"),
    ("/admin/products", "fa-box", "Products"),
    ("/admin/news", "fa-newspaper", "News"),
    ("/admin/hero", "fa-image", "Hero"),
    ("/admin/site", "fa-cog", "Site Config"),
]


def admin_layout(req, title, content):
    path = req.url.path
    def nav_link(href, icon, label):
        active = (path == href) or (href != "/admin" and path.startswith(href))
        cls = "flex items-center gap-3 px-4 py-3 rounded-lg text-gray-300 hover:bg-gray-700 hover:text-white transition"
        if active:
            cls = "flex items-center gap-3 px-4 py-3 rounded-lg bg-gray-700 text-white"
        return A(I(cls=f"fas {icon} w-5"), Span(label), href=href, cls=cls)
    sidebar = Aside(cls="w-64 fixed inset-y-0 left-0 bg-gray-800 text-white flex flex-col")(
        Div(cls="p-6 border-b border-gray-700")(
            A(cls="flex items-center gap-2 text-white hover:text-gray-300", href="/admin")(
                I(cls="fas fa-mountain text-2xl"),
                Span("Mountain Harvest", cls="font-bold text-lg"),
            ),
        ),
        Nav(cls="flex-1 p-4 space-y-1")(
            *[nav_link(href, icon, label) for href, icon, label in NAV_ITEMS],
        ),
        Div(cls="p-4 border-t border-gray-700")(
            A(cls="flex items-center gap-3 px-4 py-3 rounded-lg text-gray-300 hover:bg-gray-700 hover:text-white transition", href="/")(
                I(cls="fas fa-external-link-alt w-5"),
                Span("Về trang chủ"),
            ),
        ),
    )
    main = Main(cls="ml-64 flex-1 p-6 bg-gray-50 min-h-screen")(
        Div(cls="bg-white rounded-lg shadow p-6")(content),
    )
    return Html(
        Head(
            Title(f"{title} - Admin"),
            Link(rel="stylesheet", href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"),
        ),
        Body(
            Script(src="https://cdn.tailwindcss.com"),
            Div(cls="flex min-h-screen")(sidebar, main),
        ),
    )


# --- Admin routes (Basic Auth) ---
@rt("/admin")
def admin_index(req):
    return admin_layout(req, "Dashboard", Div(
        H1("Dashboard", cls="text-2xl font-bold mb-4 text-gray-800"),
        P("Chào mừng đến với CMS Mountain Harvest. Chọn mục trong sidebar để quản lý nội dung.", cls="text-gray-600"),
    ))


# --- Admin Products CRUD ---
PER_PAGE = 10

def _build_query_string(params: dict, updates: dict = None) -> str:
    merged = {**params}
    if updates:
        merged.update(updates)
    parts = [f"{k}={v}" for k, v in merged.items() if v]
    return "?" + "&".join(parts) if parts else ""

@rt("/admin/products")
async def admin_products(req):
    qp = req.query_params
    category = qp.get("category", "").strip()
    search = qp.get("q", "").strip()
    sort = qp.get("sort", "newest")
    page = max(1, int(qp.get("page", 1)))
    per = min(50, max(5, int(qp.get("per_page", PER_PAGE))))

    async with get_conn() as conn:
        if not conn:
            return admin_layout(req, "Products", P("Kết nối database để quản lý sản phẩm.", cls="text-amber-600"))
        cats = await conn.fetch("SELECT DISTINCT category FROM products ORDER BY category")
        categories = [r["category"] for r in cats]

        where, params = [], []
        if category:
            where.append("category = $" + str(len(params) + 1))
            params.append(category)
        if search:
            where.append("name ILIKE $" + str(len(params) + 1))
            params.append(f"%{search}%")
        where_sql = " AND ".join(where) if where else "1=1"
        order_sql = {
            "newest": "ORDER BY id DESC",
            "oldest": "ORDER BY id ASC",
            "price_asc": "ORDER BY price ASC",
            "price_desc": "ORDER BY price DESC",
            "name": "ORDER BY name ASC",
        }.get(sort, "ORDER BY id DESC")

        count_row = await conn.fetchrow(f"SELECT COUNT(*) as n FROM products WHERE {where_sql}", *params)
        total = count_row["n"]
        offset = (page - 1) * per
        rows = await conn.fetch(
            f"SELECT id, name, category, price, image FROM products WHERE {where_sql} {order_sql} LIMIT ${len(params)+1} OFFSET ${len(params)+2}",
            *params, per, offset,
        )

    total_pages = (total + per - 1) // per if total else 1
    base_params = {"category": category, "q": search, "sort": sort, "per_page": str(per)}

    filter_form = Form(method="get", action="/admin/products", cls="flex flex-wrap gap-3 items-end mb-6 p-4 bg-gray-50 rounded-lg")(
        Div(cls="flex-1 min-w-[200px]")(
            Label("Tìm kiếm", cls="block text-sm font-medium mb-1"),
            Input(name="q", value=search, placeholder="Tên sản phẩm...", cls="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"),
        ),
        Div(cls="min-w-[160px]")(
            Label("Danh mục", cls="block text-sm font-medium mb-1"),
            Select(
                *([Option("Tất cả", value="")] + [Option(c, value=c, selected=(c == category)) for c in categories]),
                name="category", cls="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm",
            ),
        ),
        Div(cls="min-w-[160px]")(
            Label("Sắp xếp", cls="block text-sm font-medium mb-1"),
            Select(
                Option("Mới nhất", value="newest", selected=(sort == "newest")),
                Option("Cũ nhất", value="oldest", selected=(sort == "oldest")),
                Option("Giá thấp → cao", value="price_asc", selected=(sort == "price_asc")),
                Option("Giá cao → thấp", value="price_desc", selected=(sort == "price_desc")),
                Option("Tên A-Z", value="name", selected=(sort == "name")),
                name="sort", cls="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm",
            ),
        ),
        Input(name="per_page", type="hidden", value=str(per)),
        Button("Lọc", type="submit", cls="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium"),
    )

    add_form = Form(method="post", action="/admin/products/new", cls="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg")(
        H2("Thêm sản phẩm", cls="text-lg font-bold mb-3 text-gray-800"),
        Div(cls="grid grid-cols-2 gap-4")(
            Div(Label("Tên", cls="block text-sm font-medium mb-1"), Input(name="name", cls="w-full border rounded px-2 py-1", required=True)),
            Div(Label("Danh mục", cls="block text-sm font-medium mb-1"), Input(name="category", cls="w-full border rounded px-2 py-1", required=True)),
            Div(Label("Giá (VNĐ)", cls="block text-sm font-medium mb-1"), Input(name="price", type="number", cls="w-full border rounded px-2 py-1", required=True)),
            Div(Label("Ảnh URL", cls="block text-sm font-medium mb-1"), Input(name="image", type="url", cls="w-full border rounded px-2 py-1")),
        ),
        Button("Thêm", type="submit", cls="mt-2 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"),
    )

    rows_html = []
    for r in rows:
        rows_html.append(Tr(cls="hover:bg-gray-50")(
            Td(r["id"], cls="px-4 py-3 border-t border-gray-200 font-mono text-gray-500 text-sm"),
            Td(r["name"], cls="px-4 py-3 border-t border-gray-200 font-medium"),
            Td(r["category"], cls="px-4 py-3 border-t border-gray-200 text-gray-600 text-sm"),
            Td(f"{r['price']:,}đ", cls="px-4 py-3 border-t border-gray-200 font-medium text-gray-800"),
            Td(Img(src=r["image"] or "", cls="w-12 h-12 object-cover rounded border") if r["image"] else Span("-", cls="text-gray-400"), cls="px-4 py-3 border-t border-gray-200"),
            Td(cls="px-4 py-3 border-t border-gray-200 whitespace-nowrap")(
                A(I(cls="fas fa-edit"), href=f"/admin/products/{r['id']}/edit", cls="inline-flex items-center gap-1 px-2 py-1 text-blue-600 hover:bg-blue-50 rounded text-sm mr-1"),
                Form(method="post", action=f"/admin/products/{r['id']}/delete", cls="inline")(
                    Button(I(cls="fas fa-trash"), type="submit", cls="inline-flex items-center gap-1 px-2 py-1 text-red-600 hover:bg-red-50 rounded text-sm", onclick="return confirm('Xóa sản phẩm này?')"),
                ),
            ),
        ))
    table = Table(cls="w-full border-collapse")(
        Thead(cls="bg-gray-100")(
            Tr(Th("ID", cls="px-4 py-3 text-left text-xs font-semibold text-gray-600"), Th("Tên", cls="px-4 py-3 text-left text-xs font-semibold text-gray-600"), Th("Danh mục", cls="px-4 py-3 text-left text-xs font-semibold text-gray-600"), Th("Giá", cls="px-4 py-3 text-left text-xs font-semibold text-gray-600"), Th("Ảnh", cls="px-4 py-3 text-left text-xs font-semibold text-gray-600"), Th("Thao tác", cls="px-4 py-3 text-left text-xs font-semibold text-gray-600")),
        ),
        Tbody(*rows_html),
    )

    pagination = []
    if total_pages > 1:
        for p in range(1, total_pages + 1):
            qs = _build_query_string(base_params, {"page": str(p)})
            if p == page:
                pagination.append(Span(str(p), cls="inline-flex items-center justify-center w-9 h-9 bg-blue-600 text-white rounded-lg font-medium"))
            else:
                pagination.append(A(str(p), href=f"/admin/products{qs}", cls="inline-flex items-center justify-center w-9 h-9 border border-gray-300 rounded-lg hover:bg-gray-100 text-gray-700"))
        pagination_html = Nav(cls="flex items-center gap-2 mt-4")(
            A(I(cls="fas fa-chevron-left"), href=f"/admin/products{_build_query_string(base_params, {'page': str(max(1, page - 1))})}", cls="p-2 rounded-lg border hover:bg-gray-100" + (" opacity-50 pointer-events-none" if page <= 1 else "")),
            *pagination,
            A(I(cls="fas fa-chevron-right"), href=f"/admin/products{_build_query_string(base_params, {'page': str(min(total_pages, page + 1))})}", cls="p-2 rounded-lg border hover:bg-gray-100" + (" opacity-50 pointer-events-none" if page >= total_pages else "")),
        )
    else:
        pagination_html = Div()

    header = Div(cls="flex flex-wrap justify-between items-center gap-4 mb-4")(
        H1("Sản phẩm", cls="text-2xl font-bold text-gray-800"),
        Span(f"{total} sản phẩm" + (f" • Trang {page}/{total_pages}" if total_pages > 1 else ""), cls="text-sm text-gray-500"),
    )
    return admin_layout(req, "Products", Div(header, filter_form, add_form, Div(cls="overflow-x-auto")(table), pagination_html))


@rt("/admin/products/new")
async def admin_product_new(req):
    form = await req.form()
    async with get_conn() as conn:
        if conn:
            await conn.execute(
                "INSERT INTO products (name, category, price, image) VALUES ($1, $2, $3, $4)",
                form.get("name", ""), form.get("category", ""), int(form.get("price", 0) or 0), form.get("image") or None,
            )
    return RedirectResponse("/admin/products", status_code=303)


@rt("/admin/products/{id:int}/edit")
async def admin_product_edit(req, id: int):
    async with get_conn() as conn:
        if not conn:
            return RedirectResponse("/admin/products")
        r = await conn.fetchrow("SELECT * FROM products WHERE id = $1", id)
    if not r:
        return RedirectResponse("/admin/products")
    tags_str = ",".join(r["tags"] or []) if isinstance(r["tags"], list) else ""
    f = Form(method="post", action=f"/admin/products/{id}", cls="space-y-4")(
        Div(Label("Tên"), Input(name="name", value=r["name"], cls="w-full border rounded px-2 py-1", required=True)),
        Div(Label("Danh mục"), Input(name="category", value=r["category"], cls="w-full border rounded px-2 py-1")),
        Div(Label("Giá"), Input(name="price", type="number", value=r["price"], cls="w-full border rounded px-2 py-1")),
        Div(Label("Giá gốc (để trống nếu không)"), Input(name="original_price", type="number", value=r["original_price"] or "", cls="w-full border rounded px-2 py-1")),
        Div(Label("Đơn vị (vd: /500g)"), Input(name="unit", value=r["unit"] or "", cls="w-full border rounded px-2 py-1")),
        Div(Label("Ảnh URL"), Input(name="image", type="url", value=r["image"] or "", cls="w-full border rounded px-2 py-1")),
        Div(Label("Mô tả"), Textarea(name="description", cls="w-full border rounded px-2 py-1", rows=4)(r["description"] or "")),
        Div(Label("Tags (phân cách bởi dấu phẩy)"), Input(name="tags", value=tags_str, cls="w-full border rounded px-2 py-1")),
        Button("Lưu", type="submit", cls="px-4 py-2 bg-blue-600 text-white rounded"),
    )
    return admin_layout(req, "Sửa sản phẩm", Div(H1("Sửa sản phẩm", cls="text-2xl font-bold mb-4"), f))


@rt("/admin/products/{id:int}")
async def admin_product_update(req, id: int):
    if req.method != "POST":
        return RedirectResponse("/admin/products")
    form = await req.form()
    tags_raw = form.get("tags") or ""
    tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
    async with get_conn() as conn:
        if conn:
            await conn.execute("""
                UPDATE products SET name=$1, category=$2, price=$3, original_price=$4, unit=$5, image=$6, description=$7, tags=$8
                WHERE id=$9
            """, form.get("name"), form.get("category"), int(form.get("price") or 0),
                int(form.get("original_price")) if form.get("original_price") else None,
                form.get("unit") or None, form.get("image") or None, form.get("description") or None,
                json.dumps(tags), id,
            )
    return RedirectResponse("/admin/products", status_code=303)


@rt("/admin/products/{id:int}/delete")
async def admin_product_delete(req, id: int):
    if req.method != "POST":
        return RedirectResponse("/admin/products")
    async with get_conn() as conn:
        if conn:
            await conn.execute("DELETE FROM products WHERE id = $1", id)
    return RedirectResponse("/admin/products", status_code=303)


# --- Admin News CRUD ---
@rt("/admin/news")
async def admin_news(req):
    qp = req.query_params
    search = qp.get("q", "").strip()
    page = max(1, int(qp.get("page", 1)))
    per = min(50, max(5, int(qp.get("per_page", PER_PAGE))))

    async with get_conn() as conn:
        if not conn:
            return admin_layout(req, "News", P("Kết nối database để quản lý tin tức.", cls="text-amber-600"))
        where, params = [], []
        if search:
            where.append("(title ILIKE $1 OR summary ILIKE $1)")
            params.append(f"%{search}%")
        where_sql = " AND ".join(where) if where else "1=1"
        count_row = await conn.fetchrow(f"SELECT COUNT(*) as n FROM news WHERE {where_sql}", *params)
        total = count_row["n"]
        offset = (page - 1) * per
        rows = await conn.fetch(
            f"SELECT id, title, date, summary, image FROM news WHERE {where_sql} ORDER BY sort_order, id DESC LIMIT ${len(params)+1} OFFSET ${len(params)+2}",
            *params, per, offset,
        )

    total_pages = (total + per - 1) // per if total else 1
    base_params = {"q": search, "per_page": str(per)}

    filter_form = Form(method="get", action="/admin/news", cls="flex flex-wrap gap-3 items-end mb-6 p-4 bg-gray-50 rounded-lg")(
        Div(cls="flex-1 min-w-[240px]")(
            Label("Tìm kiếm", cls="block text-sm font-medium mb-1"),
            Input(name="q", value=search, placeholder="Tiêu đề hoặc tóm tắt...", cls="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"),
        ),
        Input(name="per_page", type="hidden", value=str(per)),
        Button("Lọc", type="submit", cls="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium"),
    )

    add_form = Form(method="post", action="/admin/news/new", cls="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg")(
        H2("Thêm tin", cls="text-lg font-bold mb-3 text-gray-800"),
        Div(cls="grid grid-cols-2 gap-4")(
            Div(Label("Tiêu đề", cls="block text-sm font-medium mb-1"), Input(name="title", cls="w-full border rounded px-2 py-1", required=True)),
            Div(Label("Ngày (dd/mm/yyyy)", cls="block text-sm font-medium mb-1"), Input(name="date", cls="w-full border rounded px-2 py-1", placeholder="01/02/2026")),
            Div(Label("Ảnh URL", cls="block text-sm font-medium mb-1"), Input(name="image", type="url", cls="w-full border rounded px-2 py-1")),
        ),
        Div(cls="mt-2")(Label("Tóm tắt", cls="block text-sm font-medium mb-1"), Textarea(name="summary", cls="w-full border rounded px-2 py-1", rows=2)),
        Button("Thêm", type="submit", cls="mt-2 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"),
    )

    rows_html = []
    for r in rows:
        summ = (r["summary"] or "")[:60] + ("..." if (r["summary"] and len(r["summary"]) > 60) else "")
        rows_html.append(Tr(cls="hover:bg-gray-50")(
            Td(r["id"], cls="px-4 py-3 border-t border-gray-200 font-mono text-gray-500 text-sm"),
            Td(r["title"], cls="px-4 py-3 border-t border-gray-200 font-medium"),
            Td(r["date"] or "-", cls="px-4 py-3 border-t border-gray-200 text-gray-600 text-sm"),
            Td(summ, cls="px-4 py-3 border-t border-gray-200 text-gray-500 text-sm max-w-xs truncate"),
            Td(Img(src=r["image"] or "", cls="w-12 h-12 object-cover rounded border") if r.get("image") else Span("-", cls="text-gray-400"), cls="px-4 py-3 border-t border-gray-200"),
            Td(cls="px-4 py-3 border-t border-gray-200 whitespace-nowrap")(
                A(I(cls="fas fa-edit"), href=f"/admin/news/{r['id']}/edit", cls="inline-flex items-center gap-1 px-2 py-1 text-blue-600 hover:bg-blue-50 rounded text-sm mr-1"),
                Form(method="post", action=f"/admin/news/{r['id']}/delete", cls="inline")(
                    Button(I(cls="fas fa-trash"), type="submit", cls="inline-flex items-center gap-1 px-2 py-1 text-red-600 hover:bg-red-50 rounded text-sm", onclick="return confirm('Xóa tin này?')"),
                ),
            ),
        ))
    table = Table(cls="w-full border-collapse")(
        Thead(cls="bg-gray-100")(
            Tr(Th("ID", cls="px-4 py-3 text-left text-xs font-semibold text-gray-600"), Th("Tiêu đề", cls="px-4 py-3 text-left text-xs font-semibold text-gray-600"), Th("Ngày", cls="px-4 py-3 text-left text-xs font-semibold text-gray-600"), Th("Tóm tắt", cls="px-4 py-3 text-left text-xs font-semibold text-gray-600"), Th("Ảnh", cls="px-4 py-3 text-left text-xs font-semibold text-gray-600"), Th("Thao tác", cls="px-4 py-3 text-left text-xs font-semibold text-gray-600")),
        ),
        Tbody(*rows_html),
    )

    pagination = []
    if total_pages > 1:
        for p in range(1, total_pages + 1):
            qs = _build_query_string(base_params, {"page": str(p)})
            if p == page:
                pagination.append(Span(str(p), cls="inline-flex items-center justify-center w-9 h-9 bg-blue-600 text-white rounded-lg font-medium"))
            else:
                pagination.append(A(str(p), href=f"/admin/news{qs}", cls="inline-flex items-center justify-center w-9 h-9 border border-gray-300 rounded-lg hover:bg-gray-100 text-gray-700"))
        pagination_html = Nav(cls="flex items-center gap-2 mt-4")(
            A(I(cls="fas fa-chevron-left"), href=f"/admin/news{_build_query_string(base_params, {'page': str(max(1, page - 1))})}", cls="p-2 rounded-lg border hover:bg-gray-100" + (" opacity-50 pointer-events-none" if page <= 1 else "")),
            *pagination,
            A(I(cls="fas fa-chevron-right"), href=f"/admin/news{_build_query_string(base_params, {'page': str(min(total_pages, page + 1))})}", cls="p-2 rounded-lg border hover:bg-gray-100" + (" opacity-50 pointer-events-none" if page >= total_pages else "")),
        )
    else:
        pagination_html = Div()

    header = Div(cls="flex flex-wrap justify-between items-center gap-4 mb-4")(
        H1("Tin tức", cls="text-2xl font-bold text-gray-800"),
        Span(f"{total} tin" + (f" • Trang {page}/{total_pages}" if total_pages > 1 else ""), cls="text-sm text-gray-500"),
    )
    return admin_layout(req, "News", Div(header, filter_form, add_form, Div(cls="overflow-x-auto")(table), pagination_html))


@rt("/admin/news/new")
async def admin_news_new(req):
    form = await req.form()
    async with get_conn() as conn:
        if conn:
            await conn.execute("INSERT INTO news (title, image, summary, date) VALUES ($1, $2, $3, $4)",
                form.get("title"), form.get("image") or None, form.get("summary") or None, form.get("date") or None)
    return RedirectResponse("/admin/news", status_code=303)


@rt("/admin/news/{id:int}/edit")
async def admin_news_edit(req, id: int):
    async with get_conn() as conn:
        if not conn:
            return RedirectResponse("/admin/news")
        r = await conn.fetchrow("SELECT * FROM news WHERE id = $1", id)
    if not r:
        return RedirectResponse("/admin/news")
    f = Form(method="post", action=f"/admin/news/{id}", cls="space-y-4")(
        Div(Label("Tiêu đề"), Input(name="title", value=r["title"], cls="w-full border rounded px-2 py-1")),
        Div(Label("Ngày"), Input(name="date", value=r["date"] or "", cls="w-full border rounded px-2 py-1")),
        Div(Label("Ảnh URL"), Input(name="image", value=r["image"] or "", cls="w-full border rounded px-2 py-1")),
        Div(Label("Tóm tắt"), Textarea(name="summary", cls="w-full border rounded px-2 py-1", rows=4)(r["summary"] or "")),
        Button("Lưu", type="submit", cls="px-4 py-2 bg-blue-600 text-white rounded"),
    )
    return admin_layout(req, "Sửa tin", Div(H1("Sửa tin", cls="text-2xl font-bold mb-4"), f))


@rt("/admin/news/{id:int}")
async def admin_news_update(req, id: int):
    if req.method != "POST":
        return RedirectResponse("/admin/news")
    form = await req.form()
    async with get_conn() as conn:
        if conn:
            await conn.execute("UPDATE news SET title=$1, date=$2, image=$3, summary=$4 WHERE id=$5",
                form.get("title"), form.get("date") or None, form.get("image") or None, form.get("summary") or None, id)
    return RedirectResponse("/admin/news", status_code=303)


@rt("/admin/news/{id:int}/delete")
async def admin_news_delete(req, id: int):
    if req.method != "POST":
        return RedirectResponse("/admin/news")
    async with get_conn() as conn:
        if conn:
            await conn.execute("DELETE FROM news WHERE id = $1", id)
    return RedirectResponse("/admin/news", status_code=303)


# --- Admin Hero ---
@rt("/admin/hero")
async def admin_hero(req):
    async with get_conn() as conn:
        if not conn:
            return admin_layout(req, "Hero", P("Kết nối database để sửa Hero.", cls="text-amber-600"))
        r = await conn.fetchrow("SELECT promo, title, subtitle, image, button_text FROM hero LIMIT 1")
    if not r:
        r = {"promo": "", "title": "", "subtitle": "", "image": "", "button_text": ""}
    f = Form(method="post", action="/admin/hero/save", cls="space-y-4")(
        Div(Label("Promo (nhãn nhỏ)"), Input(name="promo", value=r["promo"] or "", cls="w-full border rounded px-2 py-1")),
        Div(Label("Tiêu đề"), Input(name="title", value=r["title"] or "", cls="w-full border rounded px-2 py-1")),
        Div(Label("Phụ đề"), Textarea(name="subtitle", cls="w-full border rounded px-2 py-1", rows=2)(r["subtitle"] or "")),
        Div(Label("Ảnh URL"), Input(name="image", value=r["image"] or "", cls="w-full border rounded px-2 py-1")),
        Div(Label("Nút (text)"), Input(name="button_text", value=r["button_text"] or "Shop Now", cls="w-full border rounded px-2 py-1")),
        Button("Lưu", type="submit", cls="px-4 py-2 bg-blue-600 text-white rounded"),
    )
    return admin_layout(req, "Hero", Div(H1("Hero Banner", cls="text-2xl font-bold mb-4"), f))


@rt("/admin/hero/save")
async def admin_hero_save(req):
    if req.method != "POST":
        return RedirectResponse("/admin/hero")
    form = await req.form()
    async with get_conn() as conn:
        if conn:
            await conn.execute("UPDATE hero SET promo=$1, title=$2, subtitle=$3, image=$4, button_text=$5 WHERE id=1",
                form.get("promo"), form.get("title"), form.get("subtitle"), form.get("image"), form.get("button_text"))
    return RedirectResponse("/admin/hero", status_code=303)


# --- Admin Site Config ---
@rt("/admin/site")
async def admin_site(req):
    async with get_conn() as conn:
        if not conn:
            return admin_layout(req, "Site Config", P("Kết nối database để sửa cấu hình.", cls="text-amber-600"))
        brochures = await conn.fetch("SELECT * FROM category_brochures ORDER BY id")
        config = {r["key"]: r["value"] for r in await conn.fetch("SELECT key, value FROM site_config")}
    topbar = config.get("topbar") or {}
    footer = config.get("footer") or {}
    forms = []
    forms.append(Div(cls="mb-8")(H2("Topbar", cls="text-lg font-bold mb-2"),
        Form(method="post", action="/admin/site/topbar", cls="space-y-2")(
            Div(Label("Free shipping text"), Input(name="freeShipping", value=topbar.get("freeShipping", ""), cls="w-full border rounded px-2 py-1")),
            Div(Label("Hotline"), Input(name="hotline", value=topbar.get("hotline", ""), cls="w-full border rounded px-2 py-1")),
            Button("Lưu Topbar", type="submit", cls="px-4 py-2 bg-blue-600 text-white rounded"),
        )))
    forms.append(Div(cls="mb-8")(H2("Footer", cls="text-lg font-bold mb-2"),
        Form(method="post", action="/admin/site/footer", cls="space-y-2")(
            Div(Label("Địa chỉ"), Input(name="address", value=footer.get("address", ""), cls="w-full border rounded px-2 py-1")),
            Div(Label("Điện thoại"), Input(name="phone", value=footer.get("phone", ""), cls="w-full border rounded px-2 py-1")),
            Div(Label("Email"), Input(name="email", value=footer.get("email", ""), cls="w-full border rounded px-2 py-1")),
            Button("Lưu Footer", type="submit", cls="px-4 py-2 bg-blue-600 text-white rounded"),
        )))
    for b in brochures:
        forms.append(Div(cls="mb-6 p-4 border rounded")(H2(f"Brochure: {b['slug']}", cls="text-lg font-bold mb-2"),
            Form(method="post", action=f"/admin/site/brochure/{b['slug']}", cls="space-y-2")(
                Div(Label("Tiêu đề"), Input(name="title", value=b["title"] or "", cls="w-full border rounded px-2 py-1")),
                Div(Label("Mô tả"), Input(name="desc", value=b["desc"] or "", cls="w-full border rounded px-2 py-1")),
                Div(Label("Ảnh URL"), Input(name="image", value=b["image"] or "", cls="w-full border rounded px-2 py-1")),
                Div(Label("Nút"), Input(name="button_text", value=b["button_text"] or "", cls="w-full border rounded px-2 py-1")),
                Button("Lưu", type="submit", cls="px-4 py-2 bg-blue-600 text-white rounded"),
            )))
    return admin_layout(req, "Site Config", Div(H1("Cấu hình site", cls="text-2xl font-bold mb-4"), *forms))


@rt("/admin/site/topbar")
async def admin_site_topbar(req):
    if req.method != "POST":
        return RedirectResponse("/admin/site")
    form = await req.form()
    async with get_conn() as conn:
        if conn:
            row = await conn.fetchrow("SELECT value FROM site_config WHERE key='topbar'")
            existing = dict(row["value"]) if row else {}
            existing.update({"freeShipping": form.get("freeShipping", ""), "hotline": form.get("hotline", ""), "support": form.get("support", existing.get("support", ""))})
            val = json.dumps(existing)
            await conn.execute("INSERT INTO site_config (key, value) VALUES ('topbar', $1::jsonb) ON CONFLICT (key) DO UPDATE SET value = $1::jsonb", val)
    return RedirectResponse("/admin/site", status_code=303)


@rt("/admin/site/footer")
async def admin_site_footer(req):
    if req.method != "POST":
        return RedirectResponse("/admin/site")
    form = await req.form()
    async with get_conn() as conn:
        if conn:
            row = await conn.fetchrow("SELECT value FROM site_config WHERE key='footer'")
            existing = dict(row["value"]) if row else {}
            existing.update({"address": form.get("address", ""), "phone": form.get("phone", ""), "email": form.get("email", "")})
            await conn.execute("INSERT INTO site_config (key, value) VALUES ('footer', $1::jsonb) ON CONFLICT (key) DO UPDATE SET value = $1::jsonb", json.dumps(existing))
    return RedirectResponse("/admin/site", status_code=303)


@rt("/admin/site/brochure/{slug:str}")
async def admin_site_brochure(req, slug: str):
    if req.method != "POST":
        return RedirectResponse("/admin/site")
    form = await req.form()
    async with get_conn() as conn:
        if conn:
            await conn.execute("UPDATE category_brochures SET title=$1, desc=$2, image=$3, button_text=$4 WHERE slug=$5",
                form.get("title"), form.get("desc"), form.get("image"), form.get("button_text"), slug)
    return RedirectResponse("/admin/site", status_code=303)


# Vercel: chỉ export app (ASGI). Không export handler để tránh runtime coi là BaseHTTPRequestHandler.

if __name__ == "__main__" or os.getenv("VERCEL") != "1":
    serve()
