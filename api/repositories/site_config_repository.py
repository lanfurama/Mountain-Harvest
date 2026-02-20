"""SiteConfig repository for data access."""
import json
from typing import Dict, Any, List, Optional
from api.db import get_conn
from api.models.site_config import SiteConfig


class SiteConfigRepository:
    """Repository for SiteConfig data access."""
    
    @staticmethod
    async def get_all() -> Dict[str, Any]:
        """Get all site configs."""
        async with get_conn() as conn:
            if not conn:
                return {}
            rows = await conn.fetch("SELECT key, value FROM site_config")
            return {r["key"]: r["value"] for r in rows}
    
    @staticmethod
    async def get(key: str) -> Optional[Any]:
        """Get site config by key."""
        async with get_conn() as conn:
            if not conn:
                return None
            row = await conn.fetchrow("SELECT value FROM site_config WHERE key=$1", key)
            return row["value"] if row else None
    
    @staticmethod
    async def set(key: str, value: Any) -> None:
        """Set site config."""
        async with get_conn() as conn:
            if conn:
                value_json = json.dumps(value) if not isinstance(value, str) else value
                await conn.execute(
                    "INSERT INTO site_config (key, value) VALUES ($1, $2::jsonb) ON CONFLICT (key) DO UPDATE SET value = $2::jsonb",
                    key, value_json,
                )
    
    @staticmethod
    async def update_brand(site_name: str, tagline: str, icon: str) -> None:
        """Update brand config."""
        async with get_conn() as conn:
            if conn:
                row = await conn.fetchrow("SELECT value FROM site_config WHERE key='brand'")
                existing = row["value"] if row and row["value"] is not None else {}
                if not isinstance(existing, dict):
                    existing = json.loads(existing) if isinstance(existing, str) else {}
                existing = dict(existing)
                existing.update({"siteName": site_name, "tagline": tagline, "icon": icon})
                await conn.execute(
                    "INSERT INTO site_config (key, value) VALUES ('brand', $1::jsonb) ON CONFLICT (key) DO UPDATE SET value = $1::jsonb",
                    json.dumps(existing),
                )
    
    @staticmethod
    async def update_topbar(free_shipping: str, hotline: str, support: Optional[str] = None) -> None:
        """Update topbar config."""
        async with get_conn() as conn:
            if conn:
                row = await conn.fetchrow("SELECT value FROM site_config WHERE key='topbar'")
                existing = dict(row["value"]) if row else {}
                existing.update({"freeShipping": free_shipping, "hotline": hotline, "support": support or existing.get("support", "")})
                await conn.execute(
                    "INSERT INTO site_config (key, value) VALUES ('topbar', $1::jsonb) ON CONFLICT (key) DO UPDATE SET value = $1::jsonb",
                    json.dumps(existing),
                )
    
    @staticmethod
    async def update_footer(
        address: str,
        phone: str,
        email: str,
        description: Optional[str] = None,
        copyright: Optional[str] = None,
    ) -> None:
        """Update footer config."""
        async with get_conn() as conn:
            if conn:
                row = await conn.fetchrow("SELECT value FROM site_config WHERE key='footer'")
                existing = dict(row["value"]) if row else {}
                existing.update({
                    "address": address,
                    "phone": phone,
                    "email": email,
                    "description": description or existing.get("description", ""),
                    "copyright": copyright or existing.get("copyright", ""),
                })
                await conn.execute(
                    "INSERT INTO site_config (key, value) VALUES ('footer', $1::jsonb) ON CONFLICT (key) DO UPDATE SET value = $1::jsonb",
                    json.dumps(existing),
                )
