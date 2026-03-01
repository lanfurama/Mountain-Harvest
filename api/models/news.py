"""News model."""
from django.db import models


class News(models.Model):
    """News data model."""
    title = models.CharField(max_length=255)
    image = models.TextField(null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    author = models.CharField(max_length=255, null=True, blank=True)
    date = models.CharField(max_length=20, null=True, blank=True)
    sort_order = models.IntegerField(default=0)
    meta_title = models.CharField(max_length=255, null=True, blank=True)
    meta_description = models.TextField(null=True, blank=True)
    h1_custom = models.CharField(max_length=255, null=True, blank=True)
    h2_custom = models.CharField(max_length=255, null=True, blank=True)
    h3_custom = models.CharField(max_length=255, null=True, blank=True)
    slug = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'news'
        ordering = ['-id']

    def to_dict(self):
        """Convert to dictionary for JSON response."""
        from datetime import datetime
        d = {
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
        if self.updated_at:
            d["updated_at"] = self.updated_at.isoformat()
        return d
