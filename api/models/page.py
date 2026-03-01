"""Page model."""
from django.db import models


class Page(models.Model):
    """Page (static page) data model."""
    slug = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    content = models.TextField(null=True, blank=True)
    meta_title = models.CharField(max_length=255, null=True, blank=True)
    meta_description = models.TextField(null=True, blank=True)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pages'
        ordering = ['sort_order', 'id']

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "slug": self.slug,
            "title": self.title,
            "content": self.content,
            "meta_title": self.meta_title,
            "meta_description": self.meta_description,
            "sort_order": self.sort_order,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
