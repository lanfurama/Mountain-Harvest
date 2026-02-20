"""Hero repository for data access."""
from typing import Optional
from api.db import get_conn
from api.models.hero import Hero


class HeroRepository:
    """Repository for Hero data access."""
    
    @staticmethod
    async def get() -> Optional[Hero]:
        """Get hero banner."""
        async with get_conn() as conn:
            if not conn:
                return None
            row = await conn.fetchrow("SELECT promo, title, subtitle, image, button_text FROM hero LIMIT 1")
            if not row:
                return None
            return Hero.from_db_row(row)
    
    @staticmethod
    async def get_for_edit() -> dict:
        """Get hero for editing."""
        async with get_conn() as conn:
            if not conn:
                return {"promo": "", "title": "", "subtitle": "", "image": "", "button_text": ""}
            row = await conn.fetchrow("SELECT promo, title, subtitle, image, button_text FROM hero LIMIT 1")
            if not row:
                return {"promo": "", "title": "", "subtitle": "", "image": "", "button_text": ""}
            return dict(row)
    
    @staticmethod
    async def update(
        promo: Optional[str] = None,
        title: Optional[str] = None,
        subtitle: Optional[str] = None,
        image: Optional[str] = None,
        button_text: Optional[str] = None,
    ) -> None:
        """Update hero banner."""
        async with get_conn() as conn:
            if conn:
                await conn.execute(
                    "UPDATE hero SET promo=$1, title=$2, subtitle=$3, image=$4, button_text=$5 WHERE id=1",
                    promo, title, subtitle, image, button_text,
                )
