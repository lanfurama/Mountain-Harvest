"""News service for business logic."""
from typing import List, Optional
from api.models.news import News
from api.repositories.news_repository import NewsRepository


class NewsService:
    """Service for News business logic."""
    
    @staticmethod
    async def get_news(page: int = 1, limit: int = 6) -> tuple[List[dict], int, int]:
        """Get news with pagination."""
        news_list, total = await NewsRepository.get_all(page=page, limit=limit)
        items = [n.to_dict() for n in news_list]
        total_pages = max(1, (total + limit - 1) // limit)
        return items, total, total_pages
    
    @staticmethod
    async def get_news_by_id(id: int) -> Optional[dict]:
        """Get news by ID."""
        news = await NewsRepository.get_by_id(id)
        return news.to_dict() if news else None
    
    @staticmethod
    def _mock_news() -> List[dict]:
        """Mock news for fallback."""
        return [
            {"id": 1, "title": "Mùa Thu Hoạch Bơ Sáp 034", "image": "https://images.unsplash.com/photo-1523049673856-35691f096315?ixlib=rb-1.2.1&auto=format&fit=crop&w=600&q=80",
             "content": "<p>Những trái bơ sáp 034 đầu tiên đã lên kệ.</p>", "author": "Admin", "date": "03/02/2026"},
        ]
    
    @staticmethod
    async def get_news_with_mock_fallback(page: int = 1, limit: int = 6) -> tuple[List[dict], int, int]:
        """Get news with mock fallback if database unavailable."""
        from api.db import get_conn
        async with get_conn() as conn:
            if not conn:
                all_items = NewsService._mock_news()
                total = len(all_items)
                start = (page - 1) * limit
                items = all_items[start : start + limit]
                return items, total, 1
        
        return await NewsService.get_news(page, limit)
    
    @staticmethod
    async def get_news_by_id_with_mock_fallback(id: int) -> Optional[dict]:
        """Get news by ID with mock fallback."""
        from api.db import get_conn
        async with get_conn() as conn:
            if not conn:
                for item in NewsService._mock_news():
                    if item.get("id") == id:
                        return item
                return None
        
        return await NewsService.get_news_by_id(id)
