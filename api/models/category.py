"""Category model."""
from django.db import models


class Category(models.Model):
    """Category data model."""
    name = models.CharField(max_length=100)
    sort_order = models.IntegerField(default=0)

    class Meta:
        db_table = 'categories'
        ordering = ['sort_order', 'id']

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
        }
