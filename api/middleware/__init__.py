"""Middleware package."""
from api.middleware.auth import AdminAuthMiddleware

__all__ = ["AdminAuthMiddleware"]
