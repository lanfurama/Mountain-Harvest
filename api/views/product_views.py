"""Product views for HTML rendering."""
from html import escape
import json
import re
from urllib.parse import urlparse


def _slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    if not text or not isinstance(text, str):
        return ""
    s = text.lower().strip()
    s = re.sub(r'[àáạảãâầấậẩẫăằắặẳẵ]', 'a', s)
    s = re.sub(r'[èéẹẻẽêềếệểễ]', 'e', s)
    s = re.sub(r'[ìíịỉĩ]', 'i', s)
    s = re.sub(r'[òóọỏõôồốộổỗơờớợởỡ]', 'o', s)
    s = re.sub(r'[ùúụủũưừứựửữ]', 'u', s)
    s = re.sub(r'[ỳýỵỷỹ]', 'y', s)
    s = re.sub(r'đ', 'd', s)
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'[\s_-]+', '-', s)
    return s.strip('-')


class ProductViews:
    """Views for Product HTML rendering."""

    @staticmethod
    def render_detail(base_html: str, product: dict, current_url: str) -> str:
        """Render HTML with product detail content."""
        title = escape(product.get("name", "Mountain Harvest"))
        meta_title = escape(product.get("meta_title") or title)
        h1_custom = escape(product.get("h1_custom") or title)
        h2_custom = escape(product.get("h2_custom") or "") if product.get("h2_custom") else ""
        h3_custom = escape(product.get("h3_custom") or "") if product.get("h3_custom") else ""
        image = product.get("image", "") or ""
        if image and not image.startswith(("http://", "https://")):
            parsed = urlparse(current_url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            image = base_url + ("/" + image.lstrip("/") if not image.startswith("/") else image)
        image = escape(image)
        description_raw = product.get("description", "") or ""
        category = escape(product.get("category", ""))
        price = int(product.get("price", 0))
        original_price = product.get("original_price") or product.get("originalPrice")
        unit = escape(product.get("unit", "") or "")
        meta_description = product.get("meta_description")
        if meta_description:
            description_escaped = escape(meta_description)
        else:
            desc_plain = re.sub(r'<[^>]+>', '', description_raw)
            description_escaped = escape(desc_plain[:160] if desc_plain.strip() else f"{title} - Mountain Harvest")

        page_title = f"{meta_title} - Mountain Harvest" if meta_title != title else f"{title} - Mountain Harvest"
        base_html = re.sub(r'<title>.*?</title>', f'<title>{page_title}</title>', base_html, flags=re.IGNORECASE | re.DOTALL)

        meta_tags_to_update = [
            ('name', 'description', description_escaped),
            ('property', 'og:title', meta_title),
            ('property', 'og:description', description_escaped),
            ('property', 'og:url', current_url),
            ('property', 'og:type', 'product'),
            ('name', 'twitter:title', meta_title),
            ('name', 'twitter:description', description_escaped),
            ('name', 'twitter:card', 'summary_large_image'),
        ]
        if image:
            meta_tags_to_update.extend([
                ('property', 'og:image', image),
                ('property', 'og:image:width', '1200'),
                ('property', 'og:image:height', '630'),
                ('name', 'twitter:image', image),
            ])

        for attr_type, attr_name, attr_value in meta_tags_to_update:
            if attr_type == 'property':
                pattern = rf'<meta\s+property=["\']{re.escape(attr_name)}["\'][^>]*>'
                replacement = f'<meta property="{attr_name}" content="{attr_value}">'
            else:
                pattern = rf'<meta\s+name=["\']{re.escape(attr_name)}["\'][^>]*>'
                replacement = f'<meta name="{attr_name}" content="{attr_value}">'
            if re.search(pattern, base_html, flags=re.IGNORECASE):
                base_html = re.sub(pattern, replacement, base_html, flags=re.IGNORECASE, count=1)
            else:
                base_html = base_html.replace('</head>', f'  <meta {attr_type}="{attr_name}" content="{attr_value}">\n</head>', 1)

        canonical_tag = f'<link rel="canonical" href="{escape(current_url)}">'
        if re.search(r'<link\s+rel=["\']canonical["\']', base_html, flags=re.IGNORECASE):
            base_html = re.sub(r'<link\s+rel=["\']canonical["\'][^>]*>', canonical_tag, base_html, flags=re.IGNORECASE, count=1)
        else:
            base_html = base_html.replace('</head>', f'  {canonical_tag}\n</head>', 1)

        if image:
            preload_tag = f'<link rel="preload" as="image" href="{image}" fetchpriority="high">'
            base_html = base_html.replace('</head>', preload_tag + '\n</head>', 1)

        hide_style = '<style>header.relative, #main-shop-content { display: none !important; }</style>'
        base_html = base_html.replace('</head>', hide_style + '\n</head>')

        product_schema = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": h1_custom,
            "description": description_escaped,
            "image": image if image else "",
            "category": category,
            "offers": {
                "@type": "Offer",
                "price": price,
                "priceCurrency": "VND",
                "availability": "https://schema.org/InStock",
            }
        }
        breadcrumb_schema = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Trang chủ", "item": current_url.split("/products")[0] + "/"},
                {"@type": "ListItem", "position": 2, "name": "Sản phẩm", "item": current_url.split("/products")[0] + "/#shop"},
                {"@type": "ListItem", "position": 3, "name": h1_custom},
            ]
        }
        schema_json = json.dumps(product_schema, ensure_ascii=False, indent=2)
        breadcrumb_json = json.dumps(breadcrumb_schema, ensure_ascii=False, indent=2)
        schema_script = f'<script type="application/ld+json">\n{schema_json}\n</script>\n<script type="application/ld+json">\n{breadcrumb_json}\n</script>'
        base_html = base_html.replace('</head>', schema_script + '\n</head>', 1)

        price_display = f"{price:,}đ"
        if unit:
            price_display += unit
        original_display = f"<span class=\"line-through text-gray-500 text-lg\">{original_price:,}đ</span>" if original_price and original_price > price else ""

        product_detail_html = f'''<article id="product-detail" class="w-full bg-brand-cream/40" data-server-rendered="true" itemscope itemtype="https://schema.org/Product">
      <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 md:py-12">
        <nav class="text-sm text-gray-600 mb-6" aria-label="Breadcrumb">
          <ol class="flex flex-wrap items-center gap-1">
            <li><a href="/" class="hover:text-brand-green">Trang chủ</a><span class="mx-1">/</span></li>
            <li><a href="/#shop" class="hover:text-brand-green">Sản phẩm</a><span class="mx-1">/</span></li>
            <li class="font-semibold text-gray-900">{h1_custom}</li>
          </ol>
        </nav>
        <div class="grid md:grid-cols-2 gap-8 lg:gap-12">
          <div class="relative">
            <img id="product-detail-image" src="{image}" alt="{title}" width="600" height="600" fetchpriority="high" loading="eager" class="w-full rounded-xl object-cover shadow-lg" onerror="handleImageError(this)" itemprop="image">
            {f'<span class="absolute top-4 left-4 bg-brand-orange text-white text-xs font-bold px-2 py-1 rounded">Hot</span>' if (product.get("is_hot") or product.get("isHot")) else ''}
            {f'<span class="absolute top-4 right-4 bg-red-500 text-white text-xs font-bold px-2 py-1 rounded">{escape(product.get("discount", ""))}</span>' if product.get("discount") else ''}
          </div>
          <div>
            <h1 id="product-detail-title" class="text-3xl md:text-4xl font-bold text-gray-900 mb-4" itemprop="name">{h1_custom}</h1>
            <div class="flex items-center gap-3 mb-4">
              <span class="text-brand-green font-semibold">{category}</span>
              {f'<span class="flex items-center gap-1 text-amber-500"><i class="fas fa-star"></i> {float(product.get("rating", 0))}</span>' if product.get("rating") else ''}
              {f'<span class="text-gray-500 text-sm">({product.get("reviews", 0)} đánh giá)</span>' if product.get("reviews") else ''}
            </div>
            <div class="flex flex-wrap items-baseline gap-3 mb-6">
              <span id="product-detail-price" class="text-2xl md:text-3xl font-bold text-brand-green">{price_display}</span>
              {original_display}
            </div>
            {f'<p id="product-detail-h2" class="text-xl font-semibold text-gray-800 mb-3">{h2_custom}</p>' if h2_custom else ''}
            {f'<p id="product-detail-h3" class="text-lg font-medium text-gray-700 mb-3">{h3_custom}</p>' if h3_custom else ''}
            <div id="product-detail-description" class="prose prose-lg text-gray-600 mb-8" itemprop="description">__PRODUCT_DESC__</div>
            <div class="flex flex-wrap gap-3">
              <button onclick="addToCart(this)" data-id="{product.get('id', '')}" data-name="{escape(h1_custom)}" data-price="{price}" data-image="{escape(image)}" class="inline-flex items-center gap-2 bg-brand-green hover:bg-brand-darkGreen text-white px-8 py-3 rounded-lg font-semibold transition">
                <i class="fas fa-cart-plus"></i> Thêm vào giỏ
              </button>
              <a href="/#shop" class="inline-flex items-center gap-2 border border-brand-green text-brand-green hover:bg-brand-green hover:text-white px-8 py-3 rounded-lg font-semibold transition">
                <i class="fas fa-shopping-basket"></i> Mua thêm
              </a>
            </div>
          </div>
        </div>
      </div>
    </article>'''

        product_detail_html = product_detail_html.replace("__PRODUCT_DESC__", description_raw or "<p>Liên hệ để biết thêm chi tiết.</p>")

        base_html = re.sub(
            r'<script\s+src=["\']/js/products\.js["\'][^>]*></script>',
            '<!-- products.js skipped on product page -->',
            base_html, flags=re.IGNORECASE, count=1,
        )

        product_detail_pattern = r'<article id="product-detail"[^>]*>[\s\S]*?</article>'
        if re.search(product_detail_pattern, base_html):
            base_html = re.sub(product_detail_pattern, product_detail_html, base_html, count=1)
        else:
            base_html = re.sub(r'(</main>)', product_detail_html + r'\1', base_html)

        return base_html
