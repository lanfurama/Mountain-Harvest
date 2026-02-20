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
    ):
        self.id = id
        self.title = title
        self.image = image
        self.content = content
        self.author = author
        self.date = date
        self.sort_order = sort_order
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON response."""
        return {
            "id": self.id,
            "title": self.title,
            "image": self.image,
            "content": self.content,
            "author": self.author,
            "date": self.date,
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
        )
