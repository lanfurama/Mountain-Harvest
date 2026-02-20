"""Product model."""
from typing import Optional, List


class Product:
    """Product data model."""
    
    def __init__(
        self,
        id: int,
        name: str,
        category: str,
        price: int,
        original_price: Optional[int] = None,
        unit: Optional[str] = None,
        image: Optional[str] = None,
        rating: float = 0.0,
        reviews: int = 0,
        is_hot: bool = False,
        discount: Optional[str] = None,
        tags: Optional[List[str]] = None,
        description: Optional[str] = None,
        sort_order: int = 0,
        meta_title: Optional[str] = None,
        meta_description: Optional[str] = None,
        h1_custom: Optional[str] = None,
        h2_custom: Optional[str] = None,
        h3_custom: Optional[str] = None,
    ):
        self.id = id
        self.name = name
        self.category = category
        self.price = price
        self.original_price = original_price
        self.unit = unit
        self.image = image
        self.rating = rating
        self.reviews = reviews
        self.is_hot = is_hot
        self.discount = discount
        self.tags = tags or []
        self.description = description
        self.sort_order = sort_order
        self.meta_title = meta_title
        self.meta_description = meta_description
        self.h1_custom = h1_custom
        self.h2_custom = h2_custom
        self.h3_custom = h3_custom
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON response."""
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "price": self.price,
            "originalPrice": self.original_price,
            "unit": self.unit,
            "image": self.image,
            "rating": float(self.rating or 0),
            "reviews": self.reviews or 0,
            "isHot": self.is_hot,
            "discount": self.discount,
            "tags": self.tags or [],
            "description": self.description or "",
            "meta_title": self.meta_title,
            "meta_description": self.meta_description,
            "h1_custom": self.h1_custom,
            "h2_custom": self.h2_custom,
            "h3_custom": self.h3_custom,
        }
    
    @classmethod
    def from_db_row(cls, row) -> "Product":
        """Create Product from database row."""
        return cls(
            id=row["id"],
            name=row["name"],
            category=row["category"],
            price=row["price"],
            original_price=row.get("original_price"),
            unit=row.get("unit"),
            image=row.get("image"),
            rating=float(row.get("rating") or 0),
            reviews=row.get("reviews") or 0,
            is_hot=row.get("is_hot", False),
            discount=row.get("discount"),
            tags=row.get("tags") or [],
            description=row.get("description"),
            sort_order=row.get("sort_order", 0),
            meta_title=row.get("meta_title"),
            meta_description=row.get("meta_description"),
            h1_custom=row.get("h1_custom"),
            h2_custom=row.get("h2_custom"),
            h3_custom=row.get("h3_custom"),
        )
