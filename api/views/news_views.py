"""News views for HTML rendering."""
from html import escape
import re
from urllib.parse import urlparse


class NewsViews:
    """Views for News HTML rendering."""
    
    @staticmethod
    def render_detail(base_html: str, news: dict, current_url: str) -> str:
        """Render HTML with news detail content."""
        title = escape(news.get("title", "Mountain Harvest"))
        meta_title = escape(news.get("meta_title") or title)
        h1_custom = escape(news.get("h1_custom") or title)
        h2_custom = escape(news.get("h2_custom") or "") if news.get("h2_custom") else ""
        h3_custom = escape(news.get("h3_custom") or "") if news.get("h3_custom") else ""
        image = news.get("image", "") or ""
        # Ensure image is absolute URL
        if image and not image.startswith(("http://", "https://")):
            # Extract base URL from current_url
            parsed = urlparse(current_url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            if image.startswith("/"):
                image = base_url + image
            else:
                image = base_url + "/" + image
        image = escape(image)
        content = news.get("content", "")
        author = escape(news.get("author", ""))
        date = escape(news.get("date", ""))
        
        # Use meta_description if available, otherwise extract from content
        meta_description = news.get("meta_description")
        if meta_description:
            description_escaped = escape(meta_description)
        else:
            description = re.sub(r'<[^>]+>', '', content)
            description = description.strip()[:160] if description.strip() else "Tin tức từ Mountain Harvest"
            description_escaped = escape(description)
        
        # Update title with meta_title
        page_title = f"{meta_title} - Mountain Harvest" if meta_title != title else f"{title} - Mountain Harvest"
        base_html = re.sub(r'<title>.*?</title>', f'<title>{page_title}</title>', base_html, flags=re.IGNORECASE | re.DOTALL)
        
        # Update or add meta tags - use more flexible regex that matches any content value
        meta_tags_to_update = [
            ('name', 'description', description_escaped),
            ('property', 'og:title', meta_title),
            ('property', 'og:description', description_escaped),
            ('property', 'og:url', current_url),
            ('property', 'og:type', 'article'),
            ('name', 'twitter:title', meta_title),
            ('name', 'twitter:description', description_escaped),
            ('name', 'twitter:card', 'summary_large_image'),
        ]
        
        # Add og:image and twitter:image only if cover image exists
        if image:
            meta_tags_to_update.extend([
                ('property', 'og:image', image),
                ('property', 'og:image:width', '1200'),
                ('property', 'og:image:height', '630'),
                ('name', 'twitter:image', image),
            ])
        
        for attr_type, attr_name, attr_value in meta_tags_to_update:
            # Pattern to match existing meta tag (matches any content value including empty)
            if attr_type == 'property':
                pattern = rf'<meta\s+property=["\']{re.escape(attr_name)}["\'][^>]*>'
                replacement = f'<meta property="{attr_name}" content="{attr_value}">'
            else:
                pattern = rf'<meta\s+name=["\']{re.escape(attr_name)}["\'][^>]*>'
                replacement = f'<meta name="{attr_name}" content="{attr_value}">'
            
            # Try to replace existing tag
            if re.search(pattern, base_html, flags=re.IGNORECASE):
                base_html = re.sub(pattern, replacement, base_html, flags=re.IGNORECASE, count=1)
            else:
                # Add new meta tag before </head> if not found
                new_tag = f'  <meta {attr_type}="{attr_name}" content="{attr_value}">\n'
                base_html = base_html.replace('</head>', new_tag + '</head>', 1)
        
        # Add canonical link
        canonical_tag = f'<link rel="canonical" href="{escape(current_url)}">'
        if re.search(r'<link\s+rel=["\']canonical["\']', base_html, flags=re.IGNORECASE):
            base_html = re.sub(r'<link\s+rel=["\']canonical["\'][^>]*>', canonical_tag, base_html, flags=re.IGNORECASE, count=1)
        else:
            base_html = base_html.replace('</head>', f'  {canonical_tag}\n</head>', 1)

        # Preload cover image for LCP
        if image:
            preload_tag = f'<link rel="preload" as="image" href="{image}" fetchpriority="high">'
            base_html = base_html.replace('</head>', preload_tag + '\n</head>', 1)

        # Add style to hide shop content and hero
        hide_style = '<style>header.relative, #main-shop-content { display: none !important; }</style>'
        base_html = base_html.replace('</head>', hide_style + '\n</head>')
        
        # Add Article structured data (JSON-LD)
        article_schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": h1_custom,
            "description": description_escaped,
            "image": image if image else "",
            "datePublished": date if date else "",
            "author": {
                "@type": "Person",
                "name": author if author else "Mountain Harvest"
            },
            "publisher": {
                "@type": "Organization",
                "name": "Mountain Harvest",
                "logo": {
                    "@type": "ImageObject",
                    "url": ""
                }
            }
        }
        import json
        schema_json = json.dumps(article_schema, ensure_ascii=False, indent=2)
        schema_script = f'<script type="application/ld+json">\n{schema_json}\n</script>'
        base_html = base_html.replace('</head>', schema_script + '\n</head>', 1)
        
        # Render news detail content (without hidden class)
        # Add data attribute to indicate server-rendered content
        news_detail_html = f'''<article id="news-detail" class="w-full" data-server-rendered="true">
      <div class="w-full h-[45vh] min-h-[280px] bg-gray-200 overflow-hidden">
        <img id="news-detail-image" src="{image}" alt="{title}" width="1200" height="630" fetchpriority="high" class="w-full h-full object-cover">
      </div>
      <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-10 md:py-14">
        <a href="/" class="inline-flex items-center gap-2 text-brand-green font-bold hover:underline mb-6">
          <i class="fas fa-arrow-left"></i> Quay lại tin tức
        </a>
        {f'<span id="news-detail-date" class="text-sm text-gray-500 block mb-2">{date}</span>' if date else '<span id="news-detail-date" class="text-sm text-gray-500 block mb-2"></span>'}
        {f'<span id="news-detail-author" class="text-sm text-gray-500 block mb-4">Tác giả: {author}</span>' if author else '<span id="news-detail-author" class="text-sm text-gray-500 block mb-4"></span>'}
        <h1 id="news-detail-title" class="text-3xl md:text-4xl font-bold text-gray-900 mb-6 leading-tight">{h1_custom}</h1>
        {f'<h2 id="news-detail-h2" class="text-2xl font-semibold text-gray-800 mb-4">{h2_custom}</h2>' if h2_custom else ''}
        {f'<h3 id="news-detail-h3" class="text-xl font-semibold text-gray-700 mb-3">{h3_custom}</h3>' if h3_custom else ''}
        <div id="news-detail-content" class="text-gray-600 text-lg leading-relaxed prose prose-lg max-w-none">{content}</div>
      </div>
    </article>'''
        
        # Skip products.js on news detail page to reduce payload
        base_html = re.sub(
            r'<script\s+src=["\']/js/products\.js["\'][^>]*></script>',
            '<!-- products.js skipped on news page -->',
            base_html,
            flags=re.IGNORECASE,
            count=1,
        )

        # Replace existing news-detail section (match multiline with DOTALL)
        # Pattern matches from <article id="news-detail" to closing </article>
        news_detail_pattern = r'<article id="news-detail"[^>]*>[\s\S]*?</article>'
        if re.search(news_detail_pattern, base_html):
            base_html = re.sub(
                news_detail_pattern,
                news_detail_html,
                base_html,
                count=1  # Only replace first match
            )
        else:
            # Insert before closing main tag if not found
            base_html = re.sub(
                r'(</main>)',
                news_detail_html + r'\1',
                base_html
            )
        
        return base_html
