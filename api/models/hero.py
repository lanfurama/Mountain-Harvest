"""Hero model."""
from django.db import models


class Hero(models.Model):
    """Hero banner data model."""
    promo = models.CharField(max_length=100, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    subtitle = models.TextField(null=True, blank=True)
    image = models.TextField(null=True, blank=True)
    button_text = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'hero'

    def to_dict(self):
        """Convert to dictionary for JSON response."""
        return {
            "promo": self.promo or "",
            "title": self.title or "",
            "subtitle": self.subtitle or "",
            "image": self.image or "",
            "buttonText": self.button_text or "",
        }
