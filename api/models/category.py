"""Category model."""
from typing import Optional


class Category:
    """Category data model."""
    
    def __init__(
        self,
        id: int,
        name: str,
        sort_order: int = 0,
    ):
        self.id = id
        self.name = name
        self.sort_order = sort_order
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
        }
    
    @classmethod
    def from_db_row(cls, row) -> "Category":
        """Create Category from database row."""
        return cls(
            id=row["id"],
            name=row["name"],
            sort_order=row.get("sort_order", 0),
        )
