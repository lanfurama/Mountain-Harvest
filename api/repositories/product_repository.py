"""Product repository for data access."""
import json
from typing import List, Optional
from api.db import get_conn
from api.models.product import Product


class ProductRepository:
    """Repository for Product data access."""
    
    @staticmethod
    async def get_all(
        category: Optional[str] = None,
        price: Optional[str] = None,
        standard: Optional[str] = None,
        search: Optional[str] = None,
        sort: str = "newest",
        page: int = 1,
        limit: int = 8,
    ) -> tuple[List[Product], int]:
        """Get products with filters, sorting, and pagination."""
        async with get_conn() as conn:
            if not conn:
                return [], 0
            
            base = "SELECT id, name, category, price, original_price, unit, image, rating, reviews, is_hot, discount, tags, description, meta_title, meta_description, h1_custom, h2_custom, h3_custom FROM products"
            where, params = [], []
            
            if search and search.strip():
                q = "%" + search.strip().replace("%", "\\%").replace("_", "\\_") + "%"
                where.append("(name ILIKE $" + str(len(params) + 1) + " OR COALESCE(description,'') ILIKE $" + str(len(params) + 1) + ")")
                params.append(q)
            if category:
                where.append("category = $" + str(len(params) + 1))
                params.append(category)
            if price == "under50":
                where.append("price < 50000")
            elif price == "50-200":
                where.append("price >= 50000 AND price <= 200000")
            elif price == "over200":
                where.append("price > 200000")
            if standard:
                where.append("tags @> $" + str(len(params) + 1) + "::jsonb")
                params.append(json.dumps([standard]))
            
            where_sql = " AND ".join(where) if where else "1=1"
            
            order_map = {
                "newest": "ORDER BY id DESC",
                "bestseller": "ORDER BY reviews DESC NULLS LAST, id DESC",
                "price_asc": "ORDER BY price ASC, id DESC",
                "price_desc": "ORDER BY price DESC, id DESC",
            }
            order_sql = order_map.get((sort or "newest").lower(), order_map["newest"])
            
            count_row = await conn.fetchrow(f"SELECT COUNT(*) as n FROM products WHERE {where_sql}", *params)
            total = count_row["n"] or 0
            
            offset = (page - 1) * limit
            params.extend([limit, offset])
            rows = await conn.fetch(
                f"{base} WHERE {where_sql} {order_sql} LIMIT ${len(params)-1} OFFSET ${len(params)}",
                *params,
            )
            
            products = [Product.from_db_row(row) for row in rows]
            return products, total
    
    @staticmethod
    async def get_by_id(id: int) -> Optional[Product]:
        """Get product by ID."""
        async with get_conn() as conn:
            if not conn:
                return None
            row = await conn.fetchrow(
                "SELECT id, name, category, price, original_price, unit, image, rating, reviews, is_hot, discount, tags, description, meta_title, meta_description, h1_custom, h2_custom, h3_custom FROM products WHERE id = $1",
                id,
            )
            if not row:
                return None
            return Product.from_db_row(row)
    
    @staticmethod
    async def get_categories() -> List[str]:
        """Get distinct categories."""
        async with get_conn() as conn:
            if not conn:
                return []
            rows = await conn.fetch("SELECT DISTINCT category FROM products ORDER BY category")
            return [r["category"] for r in rows]
    
    @staticmethod
    async def search(
        category: Optional[str] = None,
        search: Optional[str] = None,
        sort: str = "newest",
        page: int = 1,
        per_page: int = 10,
    ) -> tuple[List[dict], int]:
        """Search products for admin."""
        async with get_conn() as conn:
            if not conn:
                return [], 0
            
            where, params = [], []
            if category:
                where.append("category = $" + str(len(params) + 1))
                params.append(category)
            if search:
                where.append("name ILIKE $" + str(len(params) + 1))
                params.append(f"%{search}%")
            
            where_sql = " AND ".join(where) if where else "1=1"
            
            order_sql = {
                "newest": "ORDER BY id DESC",
                "oldest": "ORDER BY id ASC",
                "price_asc": "ORDER BY price ASC",
                "price_desc": "ORDER BY price DESC",
                "name": "ORDER BY name ASC",
            }.get(sort, "ORDER BY id DESC")
            
            count_row = await conn.fetchrow(f"SELECT COUNT(*) as n FROM products WHERE {where_sql}", *params)
            total = count_row["n"]
            
            offset = (page - 1) * per_page
            rows = await conn.fetch(
                f"SELECT id, name, category, price, image FROM products WHERE {where_sql} {order_sql} LIMIT ${len(params)+1} OFFSET ${len(params)+2}",
                *params, per_page, offset,
            )
            
            return [dict(row) for row in rows], total
    
    @staticmethod
    async def create(
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
        async with get_conn() as conn:
            if conn:
                await conn.execute(
                    """INSERT INTO products (name, category, price, slug, original_price, unit, image, description, tags, is_hot, discount, rating, reviews, sort_order, meta_title, meta_description, h1_custom, h2_custom, h3_custom)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19)""",
                    name, category, price, slug or None, original_price, unit or None, image or None, description or None,
                    json.dumps(tags or []), is_hot, discount or None, rating, reviews, sort_order,
                    meta_title or None, meta_description or None, h1_custom or None, h2_custom or None, h3_custom or None,
                )
    
    @staticmethod
    async def update(
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
        async with get_conn() as conn:
            if conn:
                is_hot_val = is_hot if is_hot is not None else False
                discount_val = discount
                rating_val = float(rating) if rating is not None else 0.0
                reviews_val = int(reviews) if reviews is not None else 0
                sort_order_val = int(sort_order) if sort_order is not None else 0
                await conn.execute("""
                    UPDATE products SET name=$1, category=$2, price=$3, slug=$4, original_price=$5, unit=$6, image=$7, description=$8, tags=$9, is_hot=$10, discount=$11, rating=$12, reviews=$13, sort_order=$14, meta_title=$15, meta_description=$16, h1_custom=$17, h2_custom=$18, h3_custom=$19
                    WHERE id=$20
                """, name, category, price, slug or None, original_price, unit or None, image or None, description or None,
                    json.dumps(tags or []), is_hot_val, discount_val, rating_val, reviews_val, sort_order_val,
                    meta_title or None, meta_description or None, h1_custom or None, h2_custom or None, h3_custom or None,
                    id,
                )
    
    @staticmethod
    async def get_by_id_for_edit(id: int) -> Optional[dict]:
        """Get product by ID for editing."""
        async with get_conn() as conn:
            if not conn:
                return None
            row = await conn.fetchrow("SELECT * FROM products WHERE id = $1", id)
            return dict(row) if row else None
    
    @staticmethod
    async def delete(id: int) -> None:
        """Delete a product."""
        async with get_conn() as conn:
            if conn:
                await conn.execute("DELETE FROM products WHERE id = $1", id)
