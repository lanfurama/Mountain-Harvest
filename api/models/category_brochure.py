"""CategoryBrochure model."""
from django.db import models


class CategoryBrochure(models.Model):
    """Category brochure data model."""
    slug = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    desc = models.TextField(null=True, blank=True)
    image = models.TextField(null=True, blank=True)
    button_text = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'category_brochures'
        ordering = ['id']

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "slug": self.slug,
            "title": self.title,
            "desc": self.desc,
            "image": self.image,
            "button_text": self.button_text,
        }
