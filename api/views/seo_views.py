"""SEO views for sitemap and robots."""
import os
from django.http import HttpResponse
from api.models.product import Product
from api.models.news import News
from api.models.page import Page


def _get_base_url(request) -> str:
    """Get base URL from request or env."""
    if request:
        return request.build_absolute_uri('/').rstrip('/')
    return os.getenv("SITE_URL", "https://mountainharvest.vn")


def sitemap(request):
    """Generate sitemap.xml."""
    base = _get_base_url(request)
    urls = []

    urls.append(f"""  <url>
    <loc>{base}/</loc>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>""")

    try:
        products = Product.objects.all().order_by('id')
        for p in products:
            lastmod = ""
            if p.created_at:
                try:
                    lastmod = f"\n    <lastmod>{p.created_at.strftime('%Y-%m-%d')}</lastmod>"
                except Exception:
                    pass
            urls.append(f"""  <url>
    <loc>{base}/products/{p.id}</loc>{lastmod}
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>""")

        news_items = News.objects.all().order_by('id')
        for n in news_items:
            lastmod = ""
            dt = n.updated_at or n.created_at
            if dt:
                try:
                    lastmod = f"\n    <lastmod>{dt.strftime('%Y-%m-%d')}</lastmod>"
                except Exception:
                    pass
            urls.append(f"""  <url>
    <loc>{base}/news/{n.id}</loc>{lastmod}
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>""")

        pages = Page.objects.all().order_by('sort_order')
        for p in pages:
            lastmod = ""
            if p.updated_at:
                try:
                    lastmod = f"\n    <lastmod>{p.updated_at.strftime('%Y-%m-%d')}</lastmod>"
                except Exception:
                    pass
            urls.append(f"""  <url>
    <loc>{base}/p/{p.slug}</loc>{lastmod}
    <changefreq>monthly</changefreq>
    <priority>0.5</priority>
  </url>""")
    except Exception:
        pass

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>"""
    return HttpResponse(xml, content_type="application/xml")


def robots(request):
    """Generate robots.txt."""
    base = _get_base_url(request)
    txt = f"""User-agent: *
Allow: /
Disallow: /admin

Sitemap: {base}/sitemap.xml
"""
    return HttpResponse(txt, content_type="text/plain")
