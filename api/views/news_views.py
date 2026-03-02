"""News views for HTML rendering."""
from html import escape, unescape
import re
from datetime import datetime
from urllib.parse import urlparse


def _date_to_iso(date_str: str) -> str:
    """Chuyển date DD/MM/YYYY hoặc MM/DD/YYYY sang ISO YYYY-MM-DD."""
    if not date_str or not isinstance(date_str, str):
        return ""
    s = date_str.strip()
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return ""


def normalize_content_headers(html: str) -> str:
    """Chuẩn SEO: H1->H2, H2->H3, H3->H4 trong content (page đã có H1)."""
    if not html or not isinstance(html, str):
        return html or ""
    # Thay từ cao xuống thấp để tránh replace trùng
    html = re.sub(r'<h3\b', '<h4', html, flags=re.IGNORECASE)
    html = re.sub(r'</h3>', '</h4>', html)
    html = re.sub(r'<h2\b', '<h3', html, flags=re.IGNORECASE)
    html = re.sub(r'</h2>', '</h3>', html)
    html = re.sub(r'<h1\b', '<h2', html, flags=re.IGNORECASE)
    html = re.sub(r'</h1>', '</h2>', html)
    return html


class NewsViews:
    """Views for News HTML rendering."""
    
    @staticmethod
    def render_detail(base_html: str, news: dict, current_url: str) -> str:
        """Render HTML with news detail content."""
        # Helper function to safely get and escape values
        def safe_get(key, default=""):
            value = news.get(key)
            if value is None:
                return default
            return str(value) if value else default
        
        # Helper function to get HTML content without escaping (for content field)
        def safe_get_html(key, default=""):
            value = news.get(key)
            if value is None:
                return default
            # Return as-is if it's already a string (HTML content)
            return str(value) if value else default
        
        title = escape(safe_get("title", "Mountain Harvest"))
        meta_title = escape(safe_get("meta_title") or title)
        h1_custom = escape(safe_get("h1_custom") or title)
        h2_custom = escape(safe_get("h2_custom") or "") if safe_get("h2_custom") else ""
        h3_custom = escape(safe_get("h3_custom") or "") if safe_get("h3_custom") else ""
        image = safe_get("image", "")
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
        # Get content as HTML (don't escape, it's already HTML from database)
        content_raw = safe_get_html("content", "")
        # If content appears to be escaped HTML (contains &lt; or &gt;), unescape it
        # This handles cases where content might be double-escaped
        if content_raw and ('&lt;' in content_raw or '&gt;' in content_raw or '&amp;' in content_raw):
            # Check if it's actually escaped HTML (not just contains these in text)
            if '&lt;p' in content_raw or '&lt;div' in content_raw or '&lt;h' in content_raw:
                content_raw = unescape(content_raw)
        # Normalize headers for SEO (H1->H2, H2->H3, H3->H4)
        content = normalize_content_headers(content_raw)
        author = escape(safe_get("author", ""))
        date = escape(safe_get("date", ""))
        # Estimate reading time from plain text content
        text_content = re.sub(r'<[^>]+>', '', content or '')
        word_count = len(re.findall(r'\w+', text_content))
        reading_minutes = max(1, word_count // 200) if word_count else 1
        reading_time_label = f"{reading_minutes} phút đọc"
        share_url = escape(current_url)
        
        # Use meta_description if available, otherwise extract from content
        meta_description = safe_get("meta_description", "")
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
        date_iso = _date_to_iso(date)
        date_pub_iso = date_iso + "T00:00:00+07:00" if date_iso else ""
        updated_at = news.get("updated_at") if news.get("updated_at") is not None else None
        updated_iso = ""
        if updated_at and hasattr(updated_at, 'strftime'):
            try:
                updated_iso = updated_at.strftime("%Y-%m-%dT%H:%M:%S+07:00")
            except Exception:
                updated_iso = date_pub_iso
        elif updated_at:
            updated_iso = str(updated_at)[:19].replace(" ", "T") + "+07:00" if len(str(updated_at)) >= 10 else date_pub_iso
        if not updated_iso:
            updated_iso = date_pub_iso

        meta_tags_to_update = [
            ('name', 'description', description_escaped),
            ('property', 'og:title', meta_title),
            ('property', 'og:description', description_escaped),
            ('property', 'og:url', current_url),
            ('property', 'og:type', 'article'),
            ('property', 'article:published_time', date_pub_iso) if date_pub_iso else None,
            ('property', 'article:modified_time', updated_iso) if updated_iso else None,
            ('name', 'twitter:title', meta_title),
            ('name', 'twitter:description', description_escaped),
            ('name', 'twitter:card', 'summary_large_image'),
        ]
        meta_tags_to_update = [t for t in meta_tags_to_update if t is not None]
        
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

        # Add style to hide shop content and main hero only (not news-detail header)
        hide_style = '<style>body > header, #main-shop-content { display: none !important; }</style>'
        base_html = base_html.replace('</head>', hide_style + '\n</head>')
        
        # Add Article and BreadcrumbList structured data (JSON-LD)
        article_schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": h1_custom,
            "description": description_escaped,
            "image": image if image else "",
            "datePublished": date_pub_iso,
            "dateModified": updated_iso if updated_iso else date_pub_iso,
            "author": {
                "@type": "Person",
                "name": author if author else "Mountain Harvest"
            },
            "publisher": {
                "@type": "Organization",
                "name": "Mountain Harvest",
                "logo": {"@type": "ImageObject", "url": ""}
            }
        }
        breadcrumb_schema = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Trang chủ", "item": current_url.split("/news")[0] + "/"},
                {"@type": "ListItem", "position": 2, "name": "Tin tức", "item": current_url.split("/news")[0] + "/#news-list"},
                {"@type": "ListItem", "position": 3, "name": h1_custom}
            ]
        }
        # Add Related Articles ItemList schema for SEO
        from api.services.news_service import NewsService
        news_id = news.get("id")
        related_news = []
        related_list_schema = None
        if news_id:
            try:
                related_news = NewsService.get_related_news(id=news_id, limit=3)
            except Exception:
                pass
        if related_news:
            related_list_schema = {
                "@context": "https://schema.org",
                "@type": "ItemList",
                "name": "Bài viết liên quan",
                "description": "Các bài viết tin tức liên quan khác",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": idx + 1,
                        "item": {
                            "@type": "Article",
                            "headline": r.get("title", ""),
                            "url": f"{current_url.split('/news')[0]}/news/{r.get('id')}",
                            "image": r.get("image", ""),
                            "datePublished": _date_to_iso(r.get("date", ""))
                        }
                    }
                    for idx, r in enumerate(related_news)
                ]
            }
        
        import json
        schema_json = json.dumps(article_schema, ensure_ascii=False, indent=2)
        breadcrumb_json = json.dumps(breadcrumb_schema, ensure_ascii=False, indent=2)
        schema_script = f'<script type="application/ld+json">\n{schema_json}\n</script>\n<script type="application/ld+json">\n{breadcrumb_json}\n</script>'
        if related_list_schema:
            related_json = json.dumps(related_list_schema, ensure_ascii=False, indent=2)
            schema_script += f'\n<script type="application/ld+json">\n{related_json}\n</script>'
        base_html = base_html.replace('</head>', schema_script + '\n</head>', 1)
        
        # Clean up empty paragraphs and excessive whitespace
        def clean_content_html(html_content: str) -> str:
            """Remove empty paragraphs and clean up whitespace."""
            if not html_content:
                return html_content
            # Remove empty paragraphs (with optional whitespace, <br>, &nbsp;, etc.)
            # Pattern 1: <p>...</p> with only whitespace, <br>, or &nbsp;
            html_content = re.sub(
                r'<p[^>]*>\s*(?:<br\s*/?>|\&nbsp;|\s|&nbsp;)*\s*</p>',
                '',
                html_content,
                flags=re.IGNORECASE | re.MULTILINE
            )
            # Pattern 2: <p class="...">...</p> with only whitespace
            html_content = re.sub(
                r'<p[^>]*class="[^"]*">\s*(?:<br\s*/?>|\&nbsp;|\s|&nbsp;)*\s*</p>',
                '',
                html_content,
                flags=re.IGNORECASE | re.MULTILINE
            )
            # Pattern 3: Paragraphs with only single <br> tag
            html_content = re.sub(
                r'<p[^>]*>\s*<br\s*/?>\s*</p>',
                '',
                html_content,
                flags=re.IGNORECASE | re.MULTILINE
            )
            # Pattern 4: Paragraphs with only &nbsp; entities
            html_content = re.sub(
                r'<p[^>]*>\s*(?:&nbsp;|\&#160;|\u00A0|\s)+\s*</p>',
                '',
                html_content,
                flags=re.IGNORECASE | re.MULTILINE
            )
            # Remove multiple consecutive empty paragraphs (after cleaning)
            html_content = re.sub(
                r'(</p>\s*){2,}(<p[^>]*>\s*</p>\s*)*',
                '</p>',
                html_content,
                flags=re.IGNORECASE
            )
            # Clean up excessive line breaks within content (more than 2 consecutive)
            html_content = re.sub(
                r'(<br\s*/?>\s*){3,}',
                '<br><br>',
                html_content,
                flags=re.IGNORECASE
            )
            # Remove leading/trailing empty paragraphs
            html_content = re.sub(
                r'^\s*(?:<p[^>]*>\s*</p>\s*)+',
                '',
                html_content,
                flags=re.IGNORECASE | re.MULTILINE
            )
            html_content = re.sub(
                r'(?:<p[^>]*>\s*</p>\s*)+$',
                '',
                html_content,
                flags=re.IGNORECASE | re.MULTILINE
            )
            return html_content
        
        # Process content to make images full-width
        def process_content_images(html_content: str) -> str:
            """Process content HTML to make images full-width and add responsive classes."""
            if not html_content:
                return html_content
            # Add news-content-img class to all images
            # Handle images with existing class attribute
            html_content = re.sub(
                r'<img([^>]*?)\s+class=["\']([^"\']*?)["\']([^>]*?)>',
                lambda m: f'<img{m.group(1)} class="{m.group(2)} news-content-img"{m.group(3)}>',
                html_content,
                flags=re.IGNORECASE
            )
            # Handle images without class attribute
            html_content = re.sub(
                r'<img((?:(?!\s+class=)[^>])*)>',
                r'<img class="news-content-img"\1>',
                html_content,
                flags=re.IGNORECASE
            )
            return html_content
        
        # Clean content first, then process images
        cleaned_content = clean_content_html(content)
        processed_content = process_content_images(cleaned_content)
        
        # Render news detail content (without hidden class)
        # Add data attribute to indicate server-rendered content
        news_detail_html = f'''<article id="news-detail" class="w-full bg-gradient-to-b from-brand-cream/40 to-white" data-server-rendered="true" itemscope itemtype="https://schema.org/Article">
      <header class="relative w-full h-[50vh] min-h-[320px] md:h-[60vh] md:min-h-[400px] bg-gray-900 overflow-hidden">
        <img id="news-detail-image" src="{image}" alt="{title}" width="1200" height="630" fetchpriority="high" loading="eager" class="absolute inset-0 w-full h-full object-cover transition-transform duration-700 hover:scale-105" onerror="handleImageError(this)" itemprop="image">
        <div class="absolute inset-0 bg-gradient-to-t from-black/90 via-black/50 to-black/20"></div>
        <div class="relative z-10 max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 h-full flex flex-col justify-end pb-6 md:pb-10 lg:pb-12">
          <nav class="text-xs md:text-sm text-gray-200/90 mb-4" aria-label="Breadcrumb">
            <ol class="flex flex-wrap items-center gap-1 md:gap-2">
              <li><a href="/" class="hover:text-white transition-colors">Trang chủ</a><span class="mx-1.5">/</span></li>
              <li><a href="/#news-list" class="hover:text-white transition-colors">Tin tức</a><span class="mx-1.5">/</span></li>
              <li class="font-semibold text-white line-clamp-2">{h1_custom}</li>
            </ol>
          </nav>
          <div class="flex flex-wrap items-center gap-3 md:gap-4 text-xs md:text-sm text-gray-200 mb-4">
            {f'<time id="news-detail-date" class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white/10 backdrop-blur-sm" datetime="{_date_to_iso(date)}"><i class="far fa-calendar-alt"></i> <span>{date}</span></time>' if date else '<time id="news-detail-date" class="inline-flex items-center gap-1" datetime=""></time>'}
            {f'<span id="news-detail-author" class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white/10 backdrop-blur-sm"><i class="far fa-user"></i> <span>{author}</span></span>' if author else '<span id="news-detail-author" class="inline-flex items-center gap-1"></span>'}
            <span class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white/10 backdrop-blur-sm"><i class="far fa-clock"></i> <span>{reading_time_label}</span></span>
          </div>
          <h1 id="news-detail-title" class="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold text-white leading-tight mb-0 drop-shadow-lg" itemprop="headline">{h1_custom}</h1>
        </div>
      </header>
      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 md:py-12 lg:py-16">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8 md:mb-10">
          <a href="/#news-list" class="inline-flex items-center gap-2 text-brand-green font-semibold hover:text-brand-darkGreen transition-colors group">
            <i class="fas fa-arrow-left group-hover:-translate-x-1 transition-transform"></i> <span>Quay lại tin tức</span>
          </a>
          <div class="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4">
            <span class="text-xs font-semibold text-gray-500 uppercase tracking-wide">Chia sẻ</span>
            <div class="flex items-center gap-2">
              <a href="https://www.facebook.com/sharer/sharer.php?u={share_url}" target="_blank" rel="noopener noreferrer" class="w-9 h-9 rounded-full bg-blue-600 text-white flex items-center justify-center hover:bg-blue-700 hover:scale-110 transition-all shadow-md" aria-label="Chia sẻ Facebook">
                <i class="fab fa-facebook-f text-sm"></i>
              </a>
              <a href="https://twitter.com/intent/tweet?url={share_url}&text={title}" target="_blank" rel="noopener noreferrer" class="w-9 h-9 rounded-full bg-sky-500 text-white flex items-center justify-center hover:bg-sky-600 hover:scale-110 transition-all shadow-md" aria-label="Chia sẻ Twitter">
                <i class="fab fa-x-twitter text-sm"></i>
              </a>
              <button type="button" onclick="navigator.clipboard && navigator.clipboard.writeText(window.location.href).then(() => alert('Đã sao chép link!'))" class="w-9 h-9 rounded-full bg-gray-100 text-gray-700 flex items-center justify-center hover:bg-gray-200 hover:scale-110 transition-all shadow-md" aria-label="Sao chép link">
                <i class="fas fa-link text-sm"></i>
              </button>
            </div>
          </div>
        </div>
        {f'<h2 id="news-detail-h2" class="text-2xl md:text-3xl font-bold text-gray-900 mb-6 mt-8 leading-tight">{h2_custom}</h2>' if h2_custom else ''}
        {f'<h3 id="news-detail-h3" class="text-xl md:text-2xl font-semibold text-gray-800 mb-4 mt-6 leading-tight">{h3_custom}</h3>' if h3_custom else ''}
        <div id="news-detail-content" class="news-detail-content prose prose-lg prose-headings:font-bold prose-headings:text-gray-900 prose-h2:text-2xl prose-h2:md:text-3xl prose-h2:mt-8 prose-h2:mb-4 prose-h3:text-xl prose-h3:md:text-2xl prose-h3:mt-6 prose-h3:mb-3 prose-p:text-gray-700 prose-p:leading-relaxed prose-p:text-base prose-p:md:text-lg prose-p:mb-5 prose-a:text-brand-green prose-a:font-semibold prose-a:no-underline hover:prose-a:underline prose-strong:text-gray-900 prose-strong:font-bold max-w-none" itemprop="articleBody">{processed_content}</div>
        <div class="mt-12 md:mt-16 pt-8 border-t-2 border-gray-200 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-6">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 md:w-14 md:h-14 rounded-full bg-gradient-to-br from-brand-green to-brand-darkGreen text-white flex items-center justify-center shadow-lg">
              <span class="font-bold text-base md:text-lg">{(author or "Mountain Harvest").strip()[:1].upper()}</span>
            </div>
            <div>
              <div class="text-base md:text-lg font-bold text-gray-900">
                {author or "Mountain Harvest"}
              </div>
              <p class="text-xs md:text-sm text-gray-500 mt-1">Tin tức &amp; chia sẻ từ Mountain Harvest</p>
            </div>
          </div>
          <a href="/#news-list" class="inline-flex items-center gap-2 text-sm md:text-base font-semibold text-brand-green hover:text-brand-darkGreen transition-colors group">
            <span>Xem thêm bài viết khác</span> <i class="fas fa-arrow-right group-hover:translate-x-1 transition-transform"></i>
          </a>
        </div>
      </div>
      
      <!-- Related Articles Section -->
      <section id="news-related-section" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-16 bg-white">
        <div class="mb-8 md:mb-12">
          <h2 class="text-2xl md:text-3xl font-bold text-gray-900 mb-2">Bài viết liên quan</h2>
          <p class="text-gray-600">Khám phá thêm những tin tức và câu chuyện thú vị khác</p>
        </div>
        <div id="news-related-list" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <!-- Related articles will be loaded here -->
        </div>
      </section>
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
