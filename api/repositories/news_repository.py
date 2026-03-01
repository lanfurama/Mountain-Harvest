"""News repository for data access."""
from typing import List, Optional
from django.db.models import Q
from api.models.news import News


class NewsRepository:
    """Repository for News data access."""
    
    @staticmethod
    def get_all(page: int = 1, limit: int = 6) -> tuple[List[News], int]:
        """Get all news with pagination, sorted by newest first."""
        queryset = News.objects.all()
        total = queryset.count()
        
        offset = (page - 1) * limit
        # Sort by id descending (newest first), then by sort_order if needed
        news_list = list(queryset.order_by('-id', 'sort_order')[offset:offset + limit])
        return news_list, total
    
    @staticmethod
    def get_by_id(id: int) -> Optional[News]:
        """Get news by ID."""
        try:
            return News.objects.get(id=id)
        except News.DoesNotExist:
            return None
    
    @staticmethod
    def search(
        search: Optional[str] = None,
        page: int = 1,
        per_page: int = 10,
    ) -> tuple[List[dict], int]:
        """Search news for admin."""
        queryset = News.objects.all()
        
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(content__icontains=search) | 
                Q(author__icontains=search)
            )
        
        total = queryset.count()
        
        offset = (page - 1) * per_page
        news_items = queryset.order_by('sort_order', '-id')[offset:offset + per_page]
        return [{"id": n.id, "title": n.title, "date": n.date, "author": n.author, "image": n.image} for n in news_items], total
    
    @staticmethod
    def create(
        title: str,
        slug: Optional[str] = None,
        image: Optional[str] = None,
        content: Optional[str] = None,
        author: Optional[str] = None,
        date: Optional[str] = None,
        meta_title: Optional[str] = None,
        meta_description: Optional[str] = None,
        h1_custom: Optional[str] = None,
        h2_custom: Optional[str] = None,
        h3_custom: Optional[str] = None,
    ) -> None:
        """Create a new news item."""
        News.objects.create(
            title=title,
            slug=slug,
            image=image,
            content=content,
            author=author or "Mountain Harvest",
            date=date,
            meta_title=meta_title,
            meta_description=meta_description,
            h1_custom=h1_custom,
            h2_custom=h2_custom,
            h3_custom=h3_custom,
        )
    
    @staticmethod
    def update(
        id: int,
        title: str,
        slug: Optional[str] = None,
        date: Optional[str] = None,
        image: Optional[str] = None,
        content: Optional[str] = None,
        author: Optional[str] = None,
        meta_title: Optional[str] = None,
        meta_description: Optional[str] = None,
        h1_custom: Optional[str] = None,
        h2_custom: Optional[str] = None,
        h3_custom: Optional[str] = None,
    ) -> None:
        """Update a news item."""
        news = News.objects.get(id=id)
        news.title = title
        if slug is not None:
            news.slug = slug
        if date is not None:
            news.date = date
        if image is not None:
            news.image = image
        if content is not None:
            news.content = content
        if author is not None:
            news.author = author
        if meta_title is not None:
            news.meta_title = meta_title
        if meta_description is not None:
            news.meta_description = meta_description
        if h1_custom is not None:
            news.h1_custom = h1_custom
        if h2_custom is not None:
            news.h2_custom = h2_custom
        if h3_custom is not None:
            news.h3_custom = h3_custom
        news.save()
    
    @staticmethod
    def get_by_id_for_edit(id: int) -> Optional[dict]:
        """Get news by ID for editing."""
        try:
            news = News.objects.get(id=id)
            return {
                "id": news.id,
                "title": news.title,
                "slug": news.slug,
                "image": news.image,
                "content": news.content,
                "author": news.author,
                "date": news.date,
                "meta_title": news.meta_title,
                "meta_description": news.meta_description,
                "h1_custom": news.h1_custom,
                "h2_custom": news.h2_custom,
                "h3_custom": news.h3_custom,
            }
        except News.DoesNotExist:
            return None
    
    @staticmethod
    def delete(id: int) -> None:
        """Delete a news item."""
        News.objects.filter(id=id).delete()
    
    @staticmethod
    def bulk_delete(ids: List[int]) -> None:
        """Bulk delete news items."""
        News.objects.filter(id__in=ids).delete()
