"""Product service for business logic."""
from typing import List, Optional
from api.models.product import Product
from api.repositories.product_repository import ProductRepository


class ProductService:
    """Service for Product business logic."""
    
    @staticmethod
    def apply_filters(items: List[Product], category: Optional[str], price: Optional[str], standard: Optional[str]) -> List[Product]:
        """Apply filters to product list."""
        out = items
        if category:
            out = [x for x in out if x.category == category]
        if price == "under50":
            out = [x for x in out if (x.price or 0) < 50000]
        elif price == "50-200":
            out = [x for x in out if 50000 <= (x.price or 0) <= 200000]
        elif price == "over200":
            out = [x for x in out if (x.price or 0) > 200000]
        if standard:
            tag = standard  # Organic, VietGAP, Handmade
            out = [x for x in out if tag in (x.tags or [])]
        return out
    
    @staticmethod
    def sort_products(items: List[Product], sort: str) -> List[Product]:
        """Sort products."""
        key = (sort or "newest").lower()
        if key == "bestseller":
            return sorted(items, key=lambda x: (x.reviews or 0), reverse=True)
        if key == "price_asc":
            return sorted(items, key=lambda x: (x.price or 0))
        if key == "price_desc":
            return sorted(items, key=lambda x: (x.price or 0), reverse=True)
        return sorted(items, key=lambda x: x.id, reverse=True)
    
    @staticmethod
    async def get_products(
        category: Optional[str] = None,
        price: Optional[str] = None,
        standard: Optional[str] = None,
        sort: str = "newest",
        page: int = 1,
        limit: int = 8,
    ) -> tuple[List[dict], int, int]:
        """Get products with filters, sorting, and pagination."""
        products, total = await ProductRepository.get_all(
            category=category,
            price=price,
            standard=standard,
            sort=sort,
            page=page,
            limit=limit,
        )
        items = [p.to_dict() for p in products]
        total_pages = max(1, (total + limit - 1) // limit)
        return items, total, total_pages
    
    @staticmethod
    async def get_product(id: int) -> Optional[dict]:
        """Get product by ID."""
        product = await ProductRepository.get_by_id(id)
        return product.to_dict() if product else None
    
    @staticmethod
    def _mock_products() -> List[dict]:
        """Mock products for fallback."""
        return [
            {"id": 1, "name": "Cà Chua Cherry Hữu Cơ", "category": "Rau củ quả", "price": 45000, "originalPrice": 55000,
             "unit": None, "image": "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?ixlib=rb-1.2.1&auto=format&fit=crop&w=600&q=80",
             "rating": 4.5, "reviews": 45, "isHot": False, "discount": "-15%", "tags": ["Organic"], "description": "Cà chua cherry hữu cơ."},
            {"id": 2, "name": "Gạo Lứt Đỏ Huyết Rồng", "category": "Thực phẩm khô", "price": 80000, "originalPrice": None,
             "unit": "/2kg", "image": "https://images.unsplash.com/photo-1586201375761-83865001e31c?ixlib=rb-1.2.1&auto=format&fit=crop&w=600&q=80",
             "rating": 5, "reviews": 128, "isHot": False, "discount": None, "tags": [], "description": "Gạo lứt đỏ huyết rồng."},
        ]
    
    @staticmethod
    async def get_products_with_mock_fallback(
        category: Optional[str] = None,
        price: Optional[str] = None,
        standard: Optional[str] = None,
        sort: str = "newest",
        page: int = 1,
        limit: int = 8,
    ) -> tuple[List[dict], int, int]:
        """Get products with mock fallback if database unavailable."""
        from api.db import get_conn
        async with get_conn() as conn:
            if not conn:
                all_items = ProductService._mock_products()
                # Convert mock dicts to Product objects
                products = []
                for item in all_items:
                    # Map originalPrice to original_price
                    item_dict = dict(item)
                    if "originalPrice" in item_dict:
                        item_dict["original_price"] = item_dict.pop("originalPrice")
                    if "isHot" in item_dict:
                        item_dict["is_hot"] = item_dict.pop("isHot")
                    products.append(Product(**item_dict))
                products = ProductService.apply_filters(products, category, price, standard)
                total = len(products)
                products = ProductService.sort_products(products, sort)
                start = (page - 1) * limit
                items = [p.to_dict() for p in products[start : start + limit]]
                total_pages = max(1, (total + limit - 1) // limit)
                return items, total, total_pages
        
        return await ProductService.get_products(category, price, standard, sort, page, limit)
