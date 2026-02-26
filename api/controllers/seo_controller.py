"""SEO controller for sitemap and robots."""
import os
from datetime import datetime
from starlette.responses import Response
from api.db import get_conn


def _get_base_url(req) -> str:
    """Get base URL from request or env."""
    if req:
        return str(req.base_url).rstrip("/")
    return os.getenv("SITE_URL", "https://mountainharvest.vn")


async def generate_sitemap(req) -> Response:
    """Generate sitemap.xml."""
    base = _get_base_url(req)
    urls = []

    urls.append(f"""  <url>
    <loc>{base}/</loc>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>""")

    async with get_conn() as conn:
        if conn:
            rows = await conn.fetch("SELECT id, created_at FROM products ORDER BY id")
            for r in rows:
                lastmod = ""
                if r.get("created_at"):
                    try:
                        lastmod = f"\n    <lastmod>{r['created_at'].strftime('%Y-%m-%d')}</lastmod>"
                    except Exception:
                        pass
                urls.append(f"""  <url>
    <loc>{base}/products/{r['id']}</loc>{lastmod}
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>""")

            rows = await conn.fetch("SELECT id, created_at, updated_at FROM news ORDER BY id")
            for r in rows:
                lastmod = ""
                dt = r.get("updated_at") or r.get("created_at")
                if dt:
                    try:
                        lastmod = f"\n    <lastmod>{dt.strftime('%Y-%m-%d')}</lastmod>"
                    except Exception:
                        pass
                urls.append(f"""  <url>
    <loc>{base}/news/{r['id']}</loc>{lastmod}
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>""")

            try:
                rows = await conn.fetch("SELECT slug, updated_at FROM pages ORDER BY sort_order")
                for r in rows:
                    lastmod = ""
                    if r.get("updated_at"):
                        try:
                            lastmod = f"\n    <lastmod>{r['updated_at'].strftime('%Y-%m-%d')}</lastmod>"
                        except Exception:
                            pass
                    urls.append(f"""  <url>
    <loc>{base}/p/{r['slug']}</loc>{lastmod}
    <changefreq>monthly</changefreq>
    <priority>0.5</priority>
  </url>""")
            except Exception:
                pass

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>"""
    return Response(content=xml, media_type="application/xml")


def generate_robots(req) -> Response:
    """Generate robots.txt."""
    base = _get_base_url(req)
    txt = f"""User-agent: *
Allow: /
Disallow: /admin

Sitemap: {base}/sitemap.xml
"""
    return Response(content=txt, media_type="text/plain")
