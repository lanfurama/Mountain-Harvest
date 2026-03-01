"""SiteConfig model."""
from django.db import models


class SiteConfig(models.Model):
    """Site configuration data model."""
    key = models.CharField(max_length=100, primary_key=True)
    value = models.JSONField()

    class Meta:
        db_table = 'site_config'

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "key": self.key,
            "value": self.value,
        }
