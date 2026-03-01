"""Newsletter subscriber model."""
from django.db import models


class NewsletterSubscriber(models.Model):
    """Newsletter subscriber data model."""
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'newsletter_subscribers'
        ordering = ['-created_at']
