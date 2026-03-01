"""
ASGI config for mountain_harvest project.
"""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mountain_harvest.settings')

application = get_asgi_application()
