"""Product controller."""
from starlette.responses import JSONResponse
from api.services.product_service import ProductService


class ProductController:
    """Controller for Product routes."""
    
    @staticmethod
    async def get_products(
        category: str = None,
        price: str = None,
        standard: str = None,
        sort: str = "newest",
        page: int = 1,
        limit: int = 8,
    ):
        """Get products with filters, sorting, and pagination."""
        page = max(1, page)
        limit = max(1, min(100, limit))
        items, total, total_pages = await ProductService.get_products_with_mock_fallback(
            category=category,
            price=price,
            standard=standard,
            sort=sort,
            page=page,
            limit=limit,
        )
        return JSONResponse({
            "items": items,
            "total": total,
            "page": page,
            "limit": limit,
            "totalPages": total_pages,
        })
    
    @staticmethod
    async def get_product_detail(id: int):
        """Get product by ID."""
        product = await ProductService.get_product(id)
        if not product:
            mock_products = ProductService._mock_products()
            product = next((x for x in mock_products if x["id"] == id), None)
            if not product:
                return JSONResponse({"error": "Not found"}, status_code=404)
        return JSONResponse(product)
