"""Home views for server-side HTML rendering."""
from __future__ import annotations

from typing import Dict, List
import html
import re
from urllib.parse import urlencode


class HomeViews:
    """Views for home/catalog/news list HTML rendering."""

    @staticmethod
    def _build_url(base_path: str, params: Dict[str, str]) -> str:
        params_clean = {k: v for k, v in params.items() if v not in (None, "", [])}
        if not params_clean:
            return base_path
        return base_path + "?" + urlencode(params_clean, doseq=True)

    @staticmethod
    def _render_products(items: List[dict]) -> str:
        cards: List[str] = []
        for p in items or []:
            pid = p.get("id")
            if not pid:
                continue
            name = html.escape(str(p.get("name", "")))
            category = html.escape(str(p.get("category", "")))
            image = html.escape(str(p.get("image", "")))
            price = p.get("price") or 0
            original_price = p.get("originalPrice") or p.get("original_price")
            unit = p.get("unit") or ""
            discount = p.get("discount") or ""
            tags = p.get("tags") or []
            rating = float(p.get("rating") or 0)
            reviews = int(p.get("reviews") or 0)

            # Tag badges
            tag_spans: List[str] = []
            for tag in tags:
                tag_text = html.escape(str(tag))
                color_class = "bg-blue-100 text-blue-600"
                if tag == "Best Seller":
                    color_class = "bg-brand-orange text-white"
                elif tag == "Organic":
                    color_class = "bg-green-100 text-brand-green"
                tag_spans.append(
                    f'<span class="absolute top-3 right-3 {color_class} text-xs font-bold px-2 py-1 rounded z-10 mr-1">{tag_text}</span>'
                )
            tags_html = "".join(tag_spans)

            # Rating stars
            stars: List[str] = []
            for i in range(5):
                if i < int(rating):
                    stars.append('<i class="fas fa-star"></i>')
                elif i < rating:
                    stars.append('<i class="fas fa-star-half-alt"></i>')
                else:
                    stars.append('<i class="far fa-star"></i>')
            stars_html = "".join(stars)

            # Prices
            price_html = f"{price:,.0f}đ"
            original_html = ""
            if original_price:
                original_html = f'{original_price:,.0f}đ'

            discount_html = ""
            if discount:
                discount_html = f'<span class="absolute top-3 left-3 bg-red-500 text-white text-xs font-bold px-2 py-1 rounded z-10">{html.escape(str(discount))}</span>'

            unit_html = f'<span class="text-xs text-gray-500">{html.escape(str(unit))}</span>' if unit else ""

            card = f"""
    <div class="bg-white rounded-xl shadow-sm hover:shadow-xl transition duration-300 group overflow-hidden border border-gray-100">
      <div class="relative h-64 overflow-hidden">
        {discount_html}
        {tags_html}
        <img src="{image}" class="w-full h-full object-cover transform group-hover:scale-110 transition duration-500" onerror="handleImageError(this)">
        <div class="absolute bottom-0 left-0 right-0 bg-white/90 p-2 translate-y-full group-hover:translate-y-0 transition duration-300 flex justify-center gap-2 backdrop-blur-sm">
          <!-- Quick view could be re-enabled with SSR-backed modal if needed -->
        </div>
      </div>
      <div class="p-4">
        <div class="text-xs text-gray-500 mb-1">{category}</div>
        <h3 class="font-bold text-lg text-gray-800 truncate">{name}</h3>
        <div class="flex items-center my-2">
          <div class="flex text-yellow-400 text-xs">
            {stars_html}
          </div>
          <span class="text-xs text-gray-400 ml-2">({reviews} đánh giá)</span>
        </div>
        <div class="flex justify-between items-center mt-3">
          <div>
            <span class="text-lg font-bold text-brand-green">{price_html}</span>
            {"".join([f'<span class="text-sm text-gray-400 line-through ml-2">{original_html}</span>'] if original_html else [])}
            {unit_html}
          </div>
          <button
            class="bg-brand-green text-white p-2 rounded-lg hover:bg-brand-darkGreen transition shadow-lg shadow-green-200"
            data-id="{pid}"
            data-name="{name}"
            data-price="{price}"
            data-image="{image}"
            onclick="addToCart(this)">
            <i class="fas fa-cart-plus"></i>
          </button>
        </div>
      </div>
    </div>"""
            cards.append(card)
        return "".join(cards)

    @staticmethod
    def _render_product_pagination(
        page: int,
        total_pages: int,
        base_path: str,
        filters: Dict[str, str],
        news_page: int,
    ) -> str:
        if total_pages <= 1:
            return ""
        page = max(1, min(page, total_pages))
        filters = dict(filters or {})
        html_parts: List[str] = []

        # Prev
        if page > 1:
            params = {**filters, "page": str(page - 1)}
            if news_page > 1:
                params["news_page"] = str(news_page)
            href = HomeViews._build_url(base_path, params)
            html_parts.append(
                f'<a href="{href}" class="inline-flex items-center justify-center w-9 h-9 border border-gray-300 rounded-lg hover:bg-gray-100 text-gray-700 transition"><i class="fas fa-chevron-left"></i></a>'
            )

        # Pages
        for p in range(1, total_pages + 1):
            params = {**filters, "page": str(p)}
            if news_page > 1:
                params["news_page"] = str(news_page)
            href = HomeViews._build_url(base_path, params)
            active = " bg-brand-green text-white border-brand-green" if p == page else " border-gray-300 hover:bg-gray-100 text-gray-700"
            html_parts.append(
                f'<a href="{href}" class="inline-flex items-center justify-center w-9 h-9 border rounded-lg transition{active}">{p}</a>'
            )

        # Next
        if page < total_pages:
            params = {**filters, "page": str(page + 1)}
            if news_page > 1:
                params["news_page"] = str(news_page)
            href = HomeViews._build_url(base_path, params)
            html_parts.append(
                f'<a href="{href}" class="inline-flex items-center justify-center w-9 h-9 border border-gray-300 rounded-lg hover:bg-gray-100 text-gray-700 transition"><i class="fas fa-chevron-right"></i></a>'
            )

        return "".join(html_parts)

    @staticmethod
    def _render_news(items: List[dict]) -> str:
        cards: List[str] = []
        for n in items or []:
            nid = n.get("id")
            if not nid:
                continue
            title = html.escape(str(n.get("title", "")))
            image = html.escape(str(n.get("image", "")))
            date = html.escape(str(n.get("date", "")))
            raw_content = n.get("content") or ""
            text = re.sub(r"<[^>]+>", "", raw_content)
            excerpt = html.escape(text.strip()[:150] + ("..." if len(text.strip()) > 150 else ""))
            href = f"/news/{nid}"
            card = f"""
    <div class="bg-white rounded-xl overflow-hidden shadow-sm hover:shadow-lg transition">
      <div class="h-48 overflow-hidden">
        <img src="{image}" class="w-full h-full object-cover transform hover:scale-105 transition duration-500" onerror="handleImageError(this)">
      </div>
      <div class="p-6">
        <span class="text-xs text-gray-400 mb-2 block"><i class="far fa-calendar-alt mr-1"></i> {date}</span>
        <a href="{href}" class="font-bold text-lg mb-2 hover:text-brand-green cursor-pointer block">{title}</a>
        <p class="text-gray-600 text-sm mb-4 line-clamp-3">{excerpt}</p>
      </div>
    </div>"""
            cards.append(card)
        return "".join(cards)

    @staticmethod
    def _render_news_pagination(
        page: int,
        total_pages: int,
        base_path: str,
        filters: Dict[str, str],
        news_page_param: str = "news_page",
    ) -> str:
        if total_pages <= 1:
            return ""
        page = max(1, min(page, total_pages))
        filters = dict(filters or {})
        html_parts: List[str] = []

        # Prev
        if page > 1:
            params = {**filters, news_page_param: str(page - 1)}
            href = HomeViews._build_url(base_path, params)
            html_parts.append(
                f'<a href="{href}" class="inline-flex items-center justify-center w-9 h-9 border border-gray-300 rounded-lg hover:bg-gray-100 text-gray-700 transition"><i class="fas fa-chevron-left"></i></a>'
            )

        # Pages
        for p in range(1, total_pages + 1):
            params = {**filters, news_page_param: str(p)}
            href = HomeViews._build_url(base_path, params)
            active = " bg-brand-green text-white border-brand-green" if p == page else " border-gray-300 hover:bg-gray-100 text-gray-700"
            html_parts.append(
                f'<a href="{href}" class="inline-flex items-center justify-center w-9 h-9 border rounded-lg transition{active}">{p}</a>'
            )

        # Next
        if page < total_pages:
            params = {**filters, news_page_param: str(page + 1)}
            href = HomeViews._build_url(base_path, params)
            html_parts.append(
                f'<a href="{href}" class="inline-flex items-center justify-center w-9 h-9 border border-gray-300 rounded-lg hover:bg-gray-100 text-gray-700 transition"><i class="fas fa-chevron-right"></i></a>'
            )

        return "".join(html_parts)

    @staticmethod
    def render_home(
        base_html: str,
        products_page: Dict[str, object],
        news_page: Dict[str, object],
        filters: Dict[str, str] | None = None,
        news_page_param: str = "news_page",
    ) -> str:
        """Render home page with server-side products and news."""
        filters = dict(filters or {})
        products_items = products_page.get("items") or []
        products_total_pages = int(products_page.get("total_pages") or products_page.get("totalPages") or 1)
        products_page_no = int(products_page.get("page") or 1)

        news_items = news_page.get("items") or []
        news_total_pages = int(news_page.get("total_pages") or news_page.get("totalPages") or 1)
        news_page_no = int(news_page.get("page") or 1)

        html_out = base_html

        # Replace products grid
        products_html = HomeViews._render_products(products_items)
        products_pattern = r'(<div\s+id="product-list"[^>]*>)([\s\S]*?)(</div>)'
        html_out = re.sub(
            products_pattern,
            r"\1" + products_html + r"\3",
            html_out,
            count=1,
        )

        # Replace products pagination
        prod_pagination_html = HomeViews._render_product_pagination(
            products_page_no,
            products_total_pages,
            base_path="/",
            filters=filters,
            news_page=news_page_no,
        )
        prod_pagination_pattern = r'(<div\s+id="product-pagination"[^>]*>)([\s\S]*?)(</div>)'
        html_out = re.sub(
            prod_pagination_pattern,
            r"\1" + prod_pagination_html + r"\3",
            html_out,
            count=1,
        )

        # Replace news grid
        news_html = HomeViews._render_news(news_items)
        news_pattern = r'(<div\s+id="news-list"[^>]*>)([\s\S]*?)(</div>)'
        html_out = re.sub(
            news_pattern,
            r"\1" + news_html + r"\3",
            html_out,
            count=1,
        )

        # Replace news pagination
        news_pagination_html = HomeViews._render_news_pagination(
            news_page_no,
            news_total_pages,
            base_path="/",
            filters=filters,
            news_page_param=news_page_param,
        )
        news_pagination_pattern = r'(<div\s+id="news-pagination"[^>]*>)([\s\S]*?)(</div>)'
        html_out = re.sub(
            news_pagination_pattern,
            r"\1" + news_pagination_html + r"\3",
            html_out,
            count=1,
        )

        return html_out

