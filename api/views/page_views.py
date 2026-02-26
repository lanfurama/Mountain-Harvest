"""Page views for HTML rendering."""
from html import escape
import re
from urllib.parse import urlparse


class PageViews:
    """Views for static Page HTML rendering."""

    @staticmethod
    def render_detail(base_html: str, page: dict, current_url: str) -> str:
        """Render HTML with page content."""
        title = escape(page.get("title", "Mountain Harvest"))
        meta_title = escape(page.get("meta_title") or title)
        content = page.get("content", "") or ""
        meta_description = page.get("meta_description")
        if meta_description:
            description_escaped = escape(meta_description)
        else:
            desc_plain = re.sub(r'<[^>]+>', '', content).strip()
            description_escaped = escape(desc_plain[:160] if desc_plain else f"{title} - Mountain Harvest")

        page_title = f"{meta_title} - Mountain Harvest" if meta_title != title else f"{title} - Mountain Harvest"
        base_html = re.sub(r'<title>.*?</title>', f'<title>{page_title}</title>', base_html, flags=re.IGNORECASE | re.DOTALL)

        meta_tags = [
            ('name', 'description', description_escaped),
            ('property', 'og:title', meta_title),
            ('property', 'og:description', description_escaped),
            ('property', 'og:url', current_url),
            ('property', 'og:type', 'website'),
            ('name', 'twitter:title', meta_title),
            ('name', 'twitter:description', description_escaped),
            ('name', 'twitter:card', 'summary'),
        ]
        for attr_type, attr_name, attr_value in meta_tags:
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

        hide_style = '<style>header.relative, #main-shop-content { display: none !important; }</style>'
        base_html = base_html.replace('</head>', hide_style + '\n</head>')

        page_html = f'''<article id="page-detail" class="w-full bg-brand-cream/40" data-server-rendered="true">
      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 md:py-12">
        <nav class="text-sm text-gray-600 mb-6" aria-label="Breadcrumb">
          <ol class="flex flex-wrap items-center gap-1">
            <li><a href="/" class="hover:text-brand-green">Trang chủ</a><span class="mx-1">/</span></li>
            <li class="font-semibold text-gray-900">{title}</li>
          </ol>
        </nav>
        <h1 class="text-3xl md:text-4xl font-bold text-gray-900 mb-6">{title}</h1>
        <div class="prose prose-lg max-w-none text-gray-700">__PAGE_CONTENT__</div>
      </div>
    </article>'''
        page_html = page_html.replace("__PAGE_CONTENT__", content or "<p>Nội dung đang cập nhật.</p>")

        base_html = re.sub(
            r'<script\s+src=["\']/js/products\.js["\'][^>]*></script>',
            '<!-- products.js skipped on page -->',
            base_html, flags=re.IGNORECASE, count=1,
        )

        page_pattern = r'<article id="page-detail"[^>]*>[\s\S]*?</article>'
        if re.search(page_pattern, base_html):
            base_html = re.sub(page_pattern, page_html, base_html, count=1)
        else:
            base_html = re.sub(r'(</main>)', page_html + r'\1', base_html)

        return base_html
