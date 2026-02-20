"""Site controller."""
import json
from starlette.responses import JSONResponse
from api.repositories.hero_repository import HeroRepository
from api.repositories.category_repository import CategoryRepository
from api.repositories.site_config_repository import SiteConfigRepository


class SiteController:
    """Controller for Site routes."""
    
    @staticmethod
    def _cfg(config: dict, k: str) -> dict:
        """Get config value as dict."""
        v = config.get(k)
        if v is None:
            return {}
        if isinstance(v, dict):
            return v
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}
    
    @staticmethod
    def _mock_site() -> dict:
        """Mock site data for fallback."""
        return {
            "hero": {
                "promo": "Summer Sale",
                "title": "Fresh Produce For Green Living",
                "subtitle": "Up to 20% off.",
                "image": "https://images.unsplash.com/photo-1542838132-92c53300491e?w=1920&q=80",
                "buttonText": "Shop Now"
            },
            "categories": ["Rau củ quả", "Hạt & Ngũ cốc", "Gia dụng"],
            "brochures": [
                {"slug": "fresh", "title": "Fresh Produce", "desc": "Harvested from Da Lat farms.", "image": "", "buttonText": "Shop Now"},
                {"slug": "essentials", "title": "Green Essentials", "desc": "Natural home care products.", "image": "", "buttonText": "Explore"},
            ],
            "topbar": {"freeShipping": "Free shipping for orders over 500k", "hotline": "1900 1234", "support": "Customer Support"},
            "footer": {"address": "123 Đường Mây Núi, Đà Lạt", "phone": "1900 1234", "email": "cskh@mountainharvest.vn"},
        }
    
    @staticmethod
    async def get_site():
        """Get site configuration."""
        from api.db import get_conn
        async with get_conn() as conn:
            if not conn:
                return JSONResponse(SiteController._mock_site())
        
        hero = await HeroRepository.get()
        brochures = await CategoryRepository.get_category_brochures()
        config_rows = await SiteConfigRepository.get_all()
        
        config = config_rows
        hero_dict = hero.to_dict() if hero else {}
        
        return JSONResponse({
            "hero": {
                "promo": hero_dict.get("promo", "Summer Sale"),
                "title": hero_dict.get("title", "Fresh Produce For Green Living"),
                "subtitle": hero_dict.get("subtitle", "Up to 20% off on vegetables and fruits this week."),
                "image": hero_dict.get("image", ""),
                "buttonText": hero_dict.get("buttonText", "Shop Now"),
            },
            "categories": [cat.name for cat in await CategoryRepository.get_all()],
            "brochures": [
                {"slug": b["slug"], "title": b["title"], "desc": b["desc"], "image": b["image"], "buttonText": b["button_text"]}
                for b in brochures
            ],
            "brand": SiteController._cfg(config, "brand"),
            "header": SiteController._cfg(config, "brand") or SiteController._cfg(config, "header"),
            "topbar": SiteController._cfg(config, "topbar"),
            "footer": SiteController._cfg(config, "footer"),
        })
