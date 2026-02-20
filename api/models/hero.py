"""Hero model."""
from typing import Optional


class Hero:
    """Hero banner data model."""
    
    def __init__(
        self,
        id: int = 1,
        promo: Optional[str] = None,
        title: Optional[str] = None,
        subtitle: Optional[str] = None,
        image: Optional[str] = None,
        button_text: Optional[str] = None,
    ):
        self.id = id
        self.promo = promo
        self.title = title
        self.subtitle = subtitle
        self.image = image
        self.button_text = button_text
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON response."""
        return {
            "promo": self.promo or "",
            "title": self.title or "",
            "subtitle": self.subtitle or "",
            "image": self.image or "",
            "buttonText": self.button_text or "",
        }
    
    @classmethod
    def from_db_row(cls, row) -> "Hero":
        """Create Hero from database row."""
        return cls(
            id=row.get("id", 1),
            promo=row.get("promo"),
            title=row.get("title"),
            subtitle=row.get("subtitle"),
            image=row.get("image"),
            button_text=row.get("button_text"),
        )
