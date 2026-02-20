"""News repository for data access."""
from typing import List, Optional
from api.db import get_conn
from api.models.news import News


class NewsRepository:
    """Repository for News data access."""
    
    @staticmethod
    async def get_all(page: int = 1, limit: int = 6) -> tuple[List[News], int]:
        """Get all news with pagination."""
        async with get_conn() as conn:
            if not conn:
                return [], 0
            
            count_row = await conn.fetchrow("SELECT COUNT(*) as n FROM news")
            total = count_row["n"] or 0
            
            offset = (page - 1) * limit
            rows = await conn.fetch(
                "SELECT id, title, image, content, author, date FROM news ORDER BY sort_order, id LIMIT $1 OFFSET $2",
                limit, offset,
            )
            
            news_list = [News.from_db_row(row) for row in rows]
            return news_list, total
    
    @staticmethod
    async def get_by_id(id: int) -> Optional[News]:
        """Get news by ID."""
        async with get_conn() as conn:
            if not conn:
                return None
            row = await conn.fetchrow("SELECT id, title, image, content, author, date FROM news WHERE id = $1", id)
            if not row:
                return None
            return News.from_db_row(row)
    
    @staticmethod
    async def search(
        search: Optional[str] = None,
        page: int = 1,
        per_page: int = 10,
    ) -> tuple[List[dict], int]:
        """Search news for admin."""
        async with get_conn() as conn:
            if not conn:
                return [], 0
            
            where, params = [], []
            if search:
                where.append("(title ILIKE $1 OR content ILIKE $1 OR author ILIKE $1)")
                params.append(f"%{search}%")
            
            where_sql = " AND ".join(where) if where else "1=1"
            
            count_row = await conn.fetchrow(f"SELECT COUNT(*) as n FROM news WHERE {where_sql}", *params)
            total = count_row["n"]
            
            offset = (page - 1) * per_page
            rows = await conn.fetch(
                f"SELECT id, title, date, author, image FROM news WHERE {where_sql} ORDER BY sort_order, id DESC LIMIT ${len(params)+1} OFFSET ${len(params)+2}",
                *params, per_page, offset,
            )
            
            return [dict(row) for row in rows], total
    
    @staticmethod
    async def create(
        title: str,
        image: Optional[str] = None,
        content: Optional[str] = None,
        author: Optional[str] = None,
        date: Optional[str] = None,
    ) -> None:
        """Create a new news item."""
        async with get_conn() as conn:
            if conn:
                await conn.execute(
                    "INSERT INTO news (title, image, content, author, date) VALUES ($1, $2, $3, $4, $5)",
                    title, image or None, content or None, author or "Mountain Harvest", date,
                )
    
    @staticmethod
    async def update(
        id: int,
        title: str,
        date: Optional[str] = None,
        image: Optional[str] = None,
        content: Optional[str] = None,
        author: Optional[str] = None,
    ) -> None:
        """Update a news item."""
        async with get_conn() as conn:
            if conn:
                await conn.execute(
                    "UPDATE news SET title=$1, date=$2, image=$3, content=$4, author=$5 WHERE id=$6",
                    title, date or None, image or None, content or None, author or None, id,
                )
    
    @staticmethod
    async def get_by_id_for_edit(id: int) -> Optional[dict]:
        """Get news by ID for editing."""
        async with get_conn() as conn:
            if not conn:
                return None
            row = await conn.fetchrow("SELECT * FROM news WHERE id = $1", id)
            return dict(row) if row else None
    
    @staticmethod
    async def delete(id: int) -> None:
        """Delete a news item."""
        async with get_conn() as conn:
            if conn:
                await conn.execute("DELETE FROM news WHERE id = $1", id)
