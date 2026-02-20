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
        
        # Extract description from content
        description = re.sub(r'<[^>]+>', '', content)
        description = description.strip()[:160] if description.strip() else "Tin tức từ Mountain Harvest"
        description_escaped = escape(description)
        
        # Update title
        base_html = re.sub(r'<title>.*?</title>', f'<title>{title} - Mountain Harvest</title>', base_html, flags=re.IGNORECASE | re.DOTALL)
        
        # Update or add meta tags - use more flexible regex that matches any content value
        meta_tags_to_update = [
            ('name', 'description', description_escaped),
            ('property', 'og:title', title),
            ('property', 'og:description', description_escaped),
            ('property', 'og:image', image),
            ('property', 'og:url', current_url),
            ('property', 'og:type', 'article'),
            ('name', 'twitter:title', title),
            ('name', 'twitter:description', description_escaped),
            ('name', 'twitter:image', image),
            ('name', 'twitter:card', 'summary_large_image'),
        ]
        
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
        
        # Add style to hide shop content and hero
        hide_style = '<style>header.relative, #main-shop-content { display: none !important; }</style>'
        base_html = base_html.replace('</head>', hide_style + '\n</head>')
        
        # Render news detail content (without hidden class)
        news_detail_html = f'''<article id="news-detail" class="w-full">
      <div class="w-full h-[45vh] min-h-[280px] bg-gray-200 overflow-hidden">
        <img src="{image}" alt="{title}" class="w-full h-full object-cover">
      </div>
      <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-10 md:py-14">
        <a href="/" class="inline-flex items-center gap-2 text-brand-green font-bold hover:underline mb-6">
          <i class="fas fa-arrow-left"></i> Quay lại tin tức
        </a>
        {f'<span class="text-sm text-gray-500 block mb-2">{date}</span>' if date else ''}
        {f'<span class="text-sm text-gray-500 block mb-4">Tác giả: {author}</span>' if author else ''}
        <h1 class="text-3xl md:text-4xl font-bold text-gray-900 mb-6 leading-tight">{title}</h1>
        <div class="text-gray-600 text-lg leading-relaxed prose prose-lg max-w-none">{content}</div>
      </div>
    </article>'''
        
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
