"""Category repository for data access."""
from typing import List, Optional
from api.models.category import Category
from api.models.category_brochure import CategoryBrochure


class CategoryRepository:
    """Repository for Category data access."""
    
    @staticmethod
    def get_all() -> List[Category]:
        """Get all categories."""
        return list(Category.objects.all())
    
    @staticmethod
    def get_all_rows() -> List[dict]:
        """Get all categories as dicts for admin."""
        return [{"id": c.id, "name": c.name, "sort_order": c.sort_order} for c in Category.objects.all()]
    
    @staticmethod
    def get_names() -> List[str]:
        """Get category names for dropdowns."""
        return list(Category.objects.values_list('name', flat=True).order_by('sort_order', 'id'))
    
    @staticmethod
    def get_by_id(id: int) -> Optional[dict]:
        """Get category by ID."""
        try:
            cat = Category.objects.get(id=id)
            return {"id": cat.id, "name": cat.name, "sort_order": cat.sort_order}
        except Category.DoesNotExist:
            return None
    
    @staticmethod
    def create(name: str, sort_order: int = 0) -> int:
        """Create a category. Returns new id."""
        cat = Category.objects.create(name=name, sort_order=sort_order)
        return cat.id
    
    @staticmethod
    def update(id: int, name: str, sort_order: int = 0) -> None:
        """Update a category."""
        cat = Category.objects.get(id=id)
        cat.name = name
        cat.sort_order = sort_order
        cat.save()
    
    @staticmethod
    def delete(id: int) -> None:
        """Delete a category."""
        Category.objects.filter(id=id).delete()
    
    @staticmethod
    def get_category_brochures() -> List[dict]:
        """Get category brochures."""
        return [b.to_dict() for b in CategoryBrochure.objects.all()]
    
    @staticmethod
    def get_brochures_for_admin() -> List[dict]:
        """Get brochures for admin editing."""
        return [{"id": b.id, "slug": b.slug, "title": b.title, "desc": b.desc, "image": b.image, "button_text": b.button_text} for b in CategoryBrochure.objects.all()]
    
    @staticmethod
    def update_brochure(
        slug: str,
        title: Optional[str] = None,
        desc: Optional[str] = None,
        image: Optional[str] = None,
        button_text: Optional[str] = None,
    ) -> None:
        """Update category brochure."""
        brochure, created = CategoryBrochure.objects.get_or_create(slug=slug)
        if title is not None:
            brochure.title = title
        if desc is not None:
            brochure.desc = desc
        if image is not None:
            brochure.image = image
        if button_text is not None:
            brochure.button_text = button_text
        brochure.save()
