"""Page repository for data access."""
from typing import List, Optional
from api.db import get_conn


class PageRepository:
    """Repository for Page (static pages) data access."""

    @staticmethod
    async def get_all() -> List[dict]:
        """Get all pages for admin."""
        async with get_conn() as conn:
            if not conn:
                return []
            rows = await conn.fetch("SELECT id, slug, title, meta_title, meta_description, sort_order, created_at FROM pages ORDER BY sort_order, id")
            return [dict(r) for r in rows]

    @staticmethod
    async def get_by_slug(slug: str) -> Optional[dict]:
        """Get page by slug."""
        async with get_conn() as conn:
            if not conn:
                return None
            row = await conn.fetchrow("SELECT * FROM pages WHERE slug = $1", slug)
            return dict(row) if row else None

    @staticmethod
    async def get_by_id(id: int) -> Optional[dict]:
        """Get page by ID."""
        async with get_conn() as conn:
            if not conn:
                return None
            row = await conn.fetchrow("SELECT * FROM pages WHERE id = $1", id)
            return dict(row) if row else None

    @staticmethod
    async def create(slug: str, title: str, content: Optional[str] = None, meta_title: Optional[str] = None, meta_description: Optional[str] = None, sort_order: int = 0) -> int:
        """Create a page. Returns new id."""
        async with get_conn() as conn:
            if not conn:
                return 0
            row = await conn.fetchrow(
                """INSERT INTO pages (slug, title, content, meta_title, meta_description, sort_order)
                VALUES ($1, $2, $3, $4, $5, $6) RETURNING id""",
                slug, title, content or None, meta_title or None, meta_description or None, sort_order,
            )
            return row["id"] if row else 0

    @staticmethod
    async def update(id: int, slug: str, title: str, content: Optional[str] = None, meta_title: Optional[str] = None, meta_description: Optional[str] = None, sort_order: int = 0) -> None:
        """Update a page."""
        async with get_conn() as conn:
            if conn:
                await conn.execute(
                    """UPDATE pages SET slug=$1, title=$2, content=$3, meta_title=$4, meta_description=$5, sort_order=$6, updated_at=NOW() WHERE id=$7""",
                    slug, title, content or None, meta_title or None, meta_description or None, sort_order, id,
                )

    @staticmethod
    async def delete(id: int) -> None:
        """Delete a page."""
        async with get_conn() as conn:
            if conn:
                await conn.execute("DELETE FROM pages WHERE id = $1", id)
