"""Page repository for data access."""
from typing import List, Optional
from api.models.page import Page


class PageRepository:
    """Repository for Page (static pages) data access."""

    @staticmethod
    def get_all() -> List[dict]:
        """Get all pages for admin."""
        pages = Page.objects.all()
        return [{
            "id": p.id,
            "slug": p.slug,
            "title": p.title,
            "meta_title": p.meta_title,
            "meta_description": p.meta_description,
            "sort_order": p.sort_order,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        } for p in pages]

    @staticmethod
    def get_by_slug(slug: str) -> Optional[dict]:
        """Get page by slug."""
        try:
            page = Page.objects.get(slug=slug)
            return {
                "id": page.id,
                "slug": page.slug,
                "title": page.title,
                "content": page.content,
                "meta_title": page.meta_title,
                "meta_description": page.meta_description,
                "sort_order": page.sort_order,
                "created_at": page.created_at.isoformat() if page.created_at else None,
                "updated_at": page.updated_at.isoformat() if page.updated_at else None,
            }
        except Page.DoesNotExist:
            return None

    @staticmethod
    def get_by_id(id: int) -> Optional[dict]:
        """Get page by ID."""
        try:
            page = Page.objects.get(id=id)
            return {
                "id": page.id,
                "slug": page.slug,
                "title": page.title,
                "content": page.content,
                "meta_title": page.meta_title,
                "meta_description": page.meta_description,
                "sort_order": page.sort_order,
                "created_at": page.created_at.isoformat() if page.created_at else None,
                "updated_at": page.updated_at.isoformat() if page.updated_at else None,
            }
        except Page.DoesNotExist:
            return None

    @staticmethod
    def create(slug: str, title: str, content: Optional[str] = None, meta_title: Optional[str] = None, meta_description: Optional[str] = None, sort_order: int = 0) -> int:
        """Create a page. Returns new id."""
        page = Page.objects.create(
            slug=slug,
            title=title,
            content=content,
            meta_title=meta_title,
            meta_description=meta_description,
            sort_order=sort_order,
        )
        return page.id

    @staticmethod
    def update(id: int, slug: str, title: str, content: Optional[str] = None, meta_title: Optional[str] = None, meta_description: Optional[str] = None, sort_order: int = 0) -> None:
        """Update a page."""
        page = Page.objects.get(id=id)
        page.slug = slug
        page.title = title
        page.content = content
        page.meta_title = meta_title
        page.meta_description = meta_description
        page.sort_order = sort_order
        page.save()

    @staticmethod
    def delete(id: int) -> None:
        """Delete a page."""
        Page.objects.filter(id=id).delete()
