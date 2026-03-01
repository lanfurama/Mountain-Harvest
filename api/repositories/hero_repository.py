"""Hero repository for data access."""
from typing import Optional
from api.models.hero import Hero


class HeroRepository:
    """Repository for Hero data access."""
    
    @staticmethod
    def get() -> Optional[Hero]:
        """Get hero banner."""
        return Hero.objects.first()
    
    @staticmethod
    def get_for_edit() -> dict:
        """Get hero for editing."""
        hero = Hero.objects.first()
        if hero:
            return {
                "promo": hero.promo or "",
                "title": hero.title or "",
                "subtitle": hero.subtitle or "",
                "image": hero.image or "",
                "button_text": hero.button_text or "",
            }
        return {"promo": "", "title": "", "subtitle": "", "image": "", "button_text": ""}
    
    @staticmethod
    def update(
        promo: Optional[str] = None,
        title: Optional[str] = None,
        subtitle: Optional[str] = None,
        image: Optional[str] = None,
        button_text: Optional[str] = None,
    ) -> None:
        """Update hero banner."""
        hero, created = Hero.objects.get_or_create(id=1)
        if promo is not None:
            hero.promo = promo
        if title is not None:
            hero.title = title
        if subtitle is not None:
            hero.subtitle = subtitle
        if image is not None:
            hero.image = image
        if button_text is not None:
            hero.button_text = button_text
        hero.save()
