"""News model."""
from typing import Optional


class News:
    """News data model."""
    
    def __init__(
        self,
        id: int,
        title: str,
        image: Optional[str] = None,
        content: Optional[str] = None,
        author: Optional[str] = None,
        date: Optional[str] = None,
        sort_order: int = 0,
        meta_title: Optional[str] = None,
        meta_description: Optional[str] = None,
        h1_custom: Optional[str] = None,
        h2_custom: Optional[str] = None,
        h3_custom: Optional[str] = None,
    ):
        self.id = id
        self.title = title
        self.image = image
        self.content = content
        self.author = author
        self.date = date
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
            "title": self.title,
            "image": self.image,
            "content": self.content,
            "author": self.author,
            "date": self.date,
            "meta_title": self.meta_title,
            "meta_description": self.meta_description,
            "h1_custom": self.h1_custom,
            "h2_custom": self.h2_custom,
            "h3_custom": self.h3_custom,
        }
    
    @classmethod
    def from_db_row(cls, row) -> "News":
        """Create News from database row."""
        return cls(
            id=row["id"],
            title=row["title"],
            image=row.get("image"),
            content=row.get("content"),
            author=row.get("author"),
            date=row.get("date"),
            sort_order=row.get("sort_order", 0),
            meta_title=row.get("meta_title"),
            meta_description=row.get("meta_description"),
            h1_custom=row.get("h1_custom"),
            h2_custom=row.get("h2_custom"),
            h3_custom=row.get("h3_custom"),
        )
