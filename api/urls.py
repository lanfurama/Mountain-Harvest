"""API URLs."""
from django.urls import path
from django.views.static import serve
from django.conf import settings
from django.conf.urls.static import static
from api.views import api_views, frontend_views, seo_views, admin_views_wrapper

urlpatterns = [
    # Admin routes - MUST come first to avoid matching with frontend routes
    path('admin/', admin_views_wrapper.admin_index, name='admin_index'),
    path('admin/products', admin_views_wrapper.admin_products, name='admin_products'),
    path('admin/products/new', admin_views_wrapper.admin_product_new, name='admin_product_new'),
    path('admin/products/<int:id>/edit', admin_views_wrapper.admin_product_edit, name='admin_product_edit'),
    path('admin/products/<int:id>/delete', admin_views_wrapper.admin_product_delete, name='admin_product_delete'),
    path('admin/news', admin_views_wrapper.admin_news, name='admin_news'),
    path('admin/news/add', admin_views_wrapper.admin_news_add, name='admin_news_add'),
    path('admin/news/<int:id>/edit', admin_views_wrapper.admin_news_edit, name='admin_news_edit'),
    path('admin/news/<int:id>/delete', admin_views_wrapper.admin_news_delete, name='admin_news_delete'),
    path('admin/news/bulk-delete', admin_views_wrapper.admin_news_bulk_delete, name='admin_news_bulk_delete'),
    path('admin/categories', admin_views_wrapper.admin_categories, name='admin_categories'),
    path('admin/categories/add', admin_views_wrapper.admin_category_add, name='admin_category_add'),
    path('admin/categories/<int:id>/edit', admin_views_wrapper.admin_category_edit, name='admin_category_edit'),
    path('admin/categories/<int:id>/delete', admin_views_wrapper.admin_category_delete, name='admin_category_delete'),
    path('admin/pages', admin_views_wrapper.admin_pages, name='admin_pages'),
    path('admin/pages/add', admin_views_wrapper.admin_page_add, name='admin_page_add'),
    path('admin/pages/<int:id>/edit', admin_views_wrapper.admin_page_edit, name='admin_page_edit'),
    path('admin/pages/<int:id>/delete', admin_views_wrapper.admin_page_delete, name='admin_page_delete'),
    path('admin/hero', admin_views_wrapper.admin_hero, name='admin_hero'),
    path('admin/hero/save', admin_views_wrapper.admin_hero_save, name='admin_hero_save'),
    path('admin/site', admin_views_wrapper.admin_site, name='admin_site'),
    path('admin/site/brand', admin_views_wrapper.admin_site_brand, name='admin_site_brand'),
    path('admin/site/topbar', admin_views_wrapper.admin_site_topbar, name='admin_site_topbar'),
    path('admin/site/footer', admin_views_wrapper.admin_site_footer, name='admin_site_footer'),
    path('admin/site/brochure/<str:slug>/edit', admin_views_wrapper.admin_site_brochure_edit, name='admin_site_brochure_edit'),
    
    # Frontend routes
    path('', frontend_views.index, name='index'),
    path('news/<int:id>/', frontend_views.news_detail, name='news_detail'),
    path('products/<int:id>/', frontend_views.product_detail, name='product_detail'),
    path('p/<str:slug>/', frontend_views.page_detail, name='page_detail'),
    
    # API routes
    path('api/products', api_views.api_products, name='api_products'),
    path('api/products/<int:id>', api_views.api_product_detail, name='api_product_detail'),
    path('api/news', api_views.api_news, name='api_news'),
    path('api/news/<int:id>', api_views.api_news_detail, name='api_news_detail'),
    path('api/news/<int:id>/related', api_views.api_news_related, name='api_news_related'),
    path('api/site', api_views.api_site, name='api_site'),
    path('api/pages', api_views.api_pages, name='api_pages'),
    path('api/newsletter/subscribe', api_views.api_newsletter_subscribe, name='api_newsletter_subscribe'),
    
    # SEO routes
    path('sitemap.xml', seo_views.sitemap, name='sitemap'),
    path('robots.txt', seo_views.robots, name='robots'),
]

# Serve static files in development
if settings.DEBUG:
    from pathlib import Path
    from django.views.static import serve as static_serve
    
    public_dir = Path(settings.STATICFILES_DIRS[0])
    
    def serve_css(request, filename):
        return static_serve(request, f'css/{filename}', document_root=str(public_dir))
    
    def serve_js(request, filename):
        from django.http import HttpResponse
        import os
        # Use Path.joinpath for better cross-platform compatibility
        file_path = public_dir / 'js' / filename
        if file_path.exists():
            with open(file_path, 'rb') as f:
                content = f.read()
            response = HttpResponse(content, content_type='application/javascript; charset=utf-8')
            return response
        # Fallback to static_serve
        return static_serve(request, f'js/{filename}', document_root=str(public_dir))
    
    def serve_components(request, filename):
        return static_serve(request, f'components/{filename}', document_root=str(public_dir))
    
    def serve_favicon(request):
        return static_serve(request, 'favicon.svg', document_root=str(public_dir))
    
    urlpatterns += [
        path('css/<path:filename>', serve_css),
        path('js/<path:filename>', serve_js),
        path('components/<path:filename>', serve_components),
        path('favicon.svg', serve_favicon),
    ]
