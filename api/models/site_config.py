"""SiteConfig model."""
from typing import Optional, Dict, Any


class SiteConfig:
    """Site configuration data model."""
    
    def __init__(
        self,
        key: str,
        value: Any,
    ):
        self.key = key
        self.value = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "key": self.key,
            "value": self.value,
        }
    
    @classmethod
    def from_db_row(cls, row) -> "SiteConfig":
        """Create SiteConfig from database row."""
        return cls(
            key=row["key"],
            value=row["value"],
        )
