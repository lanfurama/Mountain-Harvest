"""SiteConfig repository for data access."""
import json
from typing import Dict, Any, Optional
from api.models.site_config import SiteConfig


class SiteConfigRepository:
    """Repository for SiteConfig data access."""
    
    @staticmethod
    def get_all() -> Dict[str, Any]:
        """Get all site configs."""
        configs = SiteConfig.objects.all()
        return {c.key: c.value for c in configs}
    
    @staticmethod
    def get(key: str) -> Optional[Any]:
        """Get site config by key."""
        try:
            config = SiteConfig.objects.get(key=key)
            return config.value
        except SiteConfig.DoesNotExist:
            return None
    
    @staticmethod
    def set(key: str, value: Any) -> None:
        """Set site config."""
        SiteConfig.objects.update_or_create(
            key=key,
            defaults={'value': value}
        )
    
    @staticmethod
    def update_brand(site_name: str, tagline: str, icon: str) -> None:
        """Update brand config."""
        existing = SiteConfigRepository.get('brand') or {}
        if not isinstance(existing, dict):
            existing = json.loads(existing) if isinstance(existing, str) else {}
        existing.update({"siteName": site_name, "tagline": tagline, "icon": icon})
        SiteConfigRepository.set('brand', existing)
    
    @staticmethod
    def update_topbar(free_shipping: str, hotline: str, support: Optional[str] = None) -> None:
        """Update topbar config."""
        existing = SiteConfigRepository.get('topbar') or {}
        if not isinstance(existing, dict):
            existing = json.loads(existing) if isinstance(existing, str) else {}
        existing.update({"freeShipping": free_shipping, "hotline": hotline, "support": support or existing.get("support", "")})
        SiteConfigRepository.set('topbar', existing)
    
    @staticmethod
    def update_footer(
        address: str,
        phone: str,
        email: str,
        description: Optional[str] = None,
        copyright: Optional[str] = None,
    ) -> None:
        """Update footer config."""
        existing = SiteConfigRepository.get('footer') or {}
        if not isinstance(existing, dict):
            existing = json.loads(existing) if isinstance(existing, str) else {}
        existing.update({
            "address": address,
            "phone": phone,
            "email": email,
            "description": description or existing.get("description", ""),
            "copyright": copyright or existing.get("copyright", ""),
        })
        SiteConfigRepository.set('footer', existing)
