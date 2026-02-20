"""Category repository for data access."""
from typing import List, Optional
from api.db import get_conn
from api.models.category import Category


class CategoryRepository:
    """Repository for Category data access."""
    
    @staticmethod
    async def get_all() -> List[Category]:
        """Get all categories."""
        async with get_conn() as conn:
            if not conn:
                return []
            rows = await conn.fetch("SELECT name FROM categories ORDER BY sort_order, id")
            return [Category(id=0, name=r["name"]) for r in rows]
    
    @staticmethod
    async def get_category_brochures() -> List[dict]:
        """Get category brochures."""
        async with get_conn() as conn:
            if not conn:
                return []
            rows = await conn.fetch('SELECT slug, title, "desc", image, button_text FROM category_brochures ORDER BY id')
            return [dict(row) for row in rows]
    
    @staticmethod
    async def get_brochures_for_admin() -> List[dict]:
        """Get brochures for admin editing."""
        async with get_conn() as conn:
            if not conn:
                return []
            rows = await conn.fetch("SELECT * FROM category_brochures ORDER BY id")
            return [dict(row) for row in rows]
    
    @staticmethod
    async def update_brochure(
        slug: str,
        title: Optional[str] = None,
        desc: Optional[str] = None,
        image: Optional[str] = None,
        button_text: Optional[str] = None,
    ) -> None:
        """Update category brochure."""
        async with get_conn() as conn:
            if conn:
                await conn.execute(
                    'UPDATE category_brochures SET title=$1, "desc"=$2, image=$3, button_text=$4 WHERE slug=$5',
                    title, desc, image, button_text, slug,
                )
