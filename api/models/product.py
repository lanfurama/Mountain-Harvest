"""Product model."""
from django.db import models
from django.contrib.postgres.fields import ArrayField


class Product(models.Model):
    """Product data model."""
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    price = models.IntegerField()
    original_price = models.IntegerField(null=True, blank=True)
    unit = models.CharField(max_length=50, null=True, blank=True)
    image = models.TextField(null=True, blank=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0)
    reviews = models.IntegerField(default=0)
    is_hot = models.BooleanField(default=False)
    discount = models.CharField(max_length=20, null=True, blank=True)
    tags = ArrayField(models.CharField(max_length=50), default=list, blank=True, null=True)
    description = models.TextField(null=True, blank=True)
    sort_order = models.IntegerField(default=0)
    meta_title = models.CharField(max_length=255, null=True, blank=True)
    meta_description = models.TextField(null=True, blank=True)
    h1_custom = models.CharField(max_length=255, null=True, blank=True)
    h2_custom = models.CharField(max_length=255, null=True, blank=True)
    h3_custom = models.CharField(max_length=255, null=True, blank=True)
    slug = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'products'
        ordering = ['-id']

    def to_dict(self):
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
