"""Product repository for data access."""
import json
from typing import List, Optional
from django.db.models import Q, Count
from api.models.product import Product


class ProductRepository:
    """Repository for Product data access."""
    
    @staticmethod
    def get_all(
        category: Optional[str] = None,
        price: Optional[str] = None,
        standard: Optional[str] = None,
        search: Optional[str] = None,
        sort: str = "newest",
        page: int = 1,
        limit: int = 8,
    ) -> tuple[List[Product], int]:
        """Get products with filters, sorting, and pagination."""
        queryset = Product.objects.all()
        
        if search and search.strip():
            queryset = queryset.filter(
                Q(name__icontains=search.strip()) | 
                Q(description__icontains=search.strip())
            )
        if category:
            queryset = queryset.filter(category=category)
        if price == "under50":
            queryset = queryset.filter(price__lt=50000)
        elif price == "50-200":
            queryset = queryset.filter(price__gte=50000, price__lte=200000)
        elif price == "over200":
            queryset = queryset.filter(price__gt=200000)
        if standard:
            queryset = queryset.filter(tags__contains=[standard])
        
        total = queryset.count()
        
        order_map = {
            "newest": "-id",
            "bestseller": "-reviews",
            "price_asc": "price",
            "price_desc": "-price",
        }
        order_by = order_map.get((sort or "newest").lower(), "-id")
        queryset = queryset.order_by(order_by)
        
        offset = (page - 1) * limit
        products = list(queryset[offset:offset + limit])
        return products, total
    
    @staticmethod
    def get_by_id(id: int) -> Optional[Product]:
        """Get product by ID."""
        try:
            return Product.objects.get(id=id)
        except Product.DoesNotExist:
            return None
    
    @staticmethod
    def get_categories() -> List[str]:
        """Get distinct categories."""
        return list(Product.objects.values_list('category', flat=True).distinct().order_by('category'))
    
    @staticmethod
    def search(
        category: Optional[str] = None,
        search: Optional[str] = None,
        sort: str = "newest",
        page: int = 1,
        per_page: int = 10,
    ) -> tuple[List[dict], int]:
        """Search products for admin."""
        queryset = Product.objects.all()
        
        if category:
            queryset = queryset.filter(category=category)
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        total = queryset.count()
        
        order_map = {
            "newest": "-id",
            "oldest": "id",
            "price_asc": "price",
            "price_desc": "-price",
            "name": "name",
        }
        order_by = order_map.get(sort, "-id")
        queryset = queryset.order_by(order_by)
        
        offset = (page - 1) * per_page
        products = queryset[offset:offset + per_page]
        return [{"id": p.id, "name": p.name, "category": p.category, "price": p.price, "image": p.image} for p in products], total
    
    @staticmethod
    def create(
        name: str,
        category: str,
        price: int,
        slug: Optional[str] = None,
        original_price: Optional[int] = None,
        unit: Optional[str] = None,
        image: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        is_hot: bool = False,
        discount: Optional[str] = None,
        rating: float = 0.0,
        reviews: int = 0,
        sort_order: int = 0,
        meta_title: Optional[str] = None,
        meta_description: Optional[str] = None,
        h1_custom: Optional[str] = None,
        h2_custom: Optional[str] = None,
        h3_custom: Optional[str] = None,
    ) -> None:
        """Create a new product."""
        Product.objects.create(
            name=name,
            category=category,
            price=price,
            slug=slug,
            original_price=original_price,
            unit=unit,
            image=image,
            description=description,
            tags=tags or [],
            is_hot=is_hot,
            discount=discount,
            rating=rating,
            reviews=reviews,
            sort_order=sort_order,
            meta_title=meta_title,
            meta_description=meta_description,
            h1_custom=h1_custom,
            h2_custom=h2_custom,
            h3_custom=h3_custom,
        )
    
    @staticmethod
    def update(
        id: int,
        name: str,
        category: str,
        price: int,
        slug: Optional[str] = None,
        original_price: Optional[int] = None,
        unit: Optional[str] = None,
        image: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        is_hot: Optional[bool] = None,
        discount: Optional[str] = None,
        rating: Optional[float] = None,
        reviews: Optional[int] = None,
        sort_order: Optional[int] = None,
        meta_title: Optional[str] = None,
        meta_description: Optional[str] = None,
        h1_custom: Optional[str] = None,
        h2_custom: Optional[str] = None,
        h3_custom: Optional[str] = None,
    ) -> None:
        """Update a product."""
        product = Product.objects.get(id=id)
        product.name = name
        product.category = category
        product.price = price
        if slug is not None:
            product.slug = slug
        if original_price is not None:
            product.original_price = original_price
        if unit is not None:
            product.unit = unit
        if image is not None:
            product.image = image
        if description is not None:
            product.description = description
        if tags is not None:
            product.tags = tags
        if is_hot is not None:
            product.is_hot = is_hot
        if discount is not None:
            product.discount = discount
        if rating is not None:
            product.rating = rating
        if reviews is not None:
            product.reviews = reviews
        if sort_order is not None:
            product.sort_order = sort_order
        if meta_title is not None:
            product.meta_title = meta_title
        if meta_description is not None:
            product.meta_description = meta_description
        if h1_custom is not None:
            product.h1_custom = h1_custom
        if h2_custom is not None:
            product.h2_custom = h2_custom
        if h3_custom is not None:
            product.h3_custom = h3_custom
        product.save()
    
    @staticmethod
    def get_by_id_for_edit(id: int) -> Optional[dict]:
        """Get product by ID for editing."""
        try:
            product = Product.objects.get(id=id)
            return {
                "id": product.id,
                "name": product.name,
                "category": product.category,
                "price": product.price,
                "slug": product.slug,
                "original_price": product.original_price,
                "unit": product.unit,
                "image": product.image,
                "description": product.description,
                "tags": product.tags,
                "is_hot": product.is_hot,
                "discount": product.discount,
                "rating": float(product.rating),
                "reviews": product.reviews,
                "sort_order": product.sort_order,
                "meta_title": product.meta_title,
                "meta_description": product.meta_description,
                "h1_custom": product.h1_custom,
                "h2_custom": product.h2_custom,
                "h3_custom": product.h3_custom,
            }
        except Product.DoesNotExist:
            return None
    
    @staticmethod
    def delete(id: int) -> None:
        """Delete a product."""
        Product.objects.filter(id=id).delete()
