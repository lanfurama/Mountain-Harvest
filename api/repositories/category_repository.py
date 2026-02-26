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
            rows = await conn.fetch("SELECT id, name, sort_order FROM categories ORDER BY sort_order, id")
            return [Category.from_db_row(r) for r in rows]
    
    @staticmethod
    async def get_all_rows() -> List[dict]:
        """Get all categories as dicts for admin."""
        async with get_conn() as conn:
            if not conn:
                return []
            rows = await conn.fetch("SELECT id, name, sort_order FROM categories ORDER BY sort_order, id")
            return [dict(r) for r in rows]
    
    @staticmethod
    async def get_names() -> List[str]:
        """Get category names for dropdowns."""
        async with get_conn() as conn:
            if not conn:
                return []
            rows = await conn.fetch("SELECT name FROM categories ORDER BY sort_order, id")
            return [r["name"] for r in rows]
    
    @staticmethod
    async def get_by_id(id: int) -> Optional[dict]:
        """Get category by ID."""
        async with get_conn() as conn:
            if not conn:
                return None
            row = await conn.fetchrow("SELECT * FROM categories WHERE id = $1", id)
            return dict(row) if row else None
    
    @staticmethod
    async def create(name: str, sort_order: int = 0) -> int:
        """Create a category. Returns new id."""
        async with get_conn() as conn:
            if not conn:
                return 0
            row = await conn.fetchrow(
                "INSERT INTO categories (name, sort_order) VALUES ($1, $2) RETURNING id",
                name, sort_order,
            )
            return row["id"] if row else 0
    
    @staticmethod
    async def update(id: int, name: str, sort_order: int = 0) -> None:
        """Update a category."""
        async with get_conn() as conn:
            if conn:
                await conn.execute(
                    "UPDATE categories SET name=$1, sort_order=$2 WHERE id=$3",
                    name, sort_order, id,
                )
    
    @staticmethod
    async def delete(id: int) -> None:
        """Delete a category."""
        async with get_conn() as conn:
            if conn:
                await conn.execute("DELETE FROM categories WHERE id = $1", id)
    
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
