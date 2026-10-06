import base64
import json
import logging
from datetime import datetime
from decimal import Decimal, InvalidOperation

from sqlalchemy import select, func, or_, and_, asc, desc
from sqlalchemy.orm import Session, selectinload

from app.models import Product, Brand, Category, ProductImage, ProductVariant, VariantAttribute, VendorProduct, ProductReview
from app.utils.pagination import encode_cursor, decode_cursor

log = logging.getLogger(__name__)

SORT_MAP = {
    "newest": ("created_at", "desc"),
    "oldest": ("created_at", "asc"),
    "price_asc": ("price", "asc"),
    "price_desc": ("price", "desc"),
    "rating": ("rating", "desc"),
    "popularity": ("review_count", "desc"),
    "name_asc": ("name", "asc"),
    "name_desc": ("name", "desc"),
}

SORT_COLUMNS = {
    "created_at": Product.created_at,
    "price": Product.price,
    "rating": Product.rating,
    "review_count": Product.review_count,
    "name": Product.name,
}


def _base_filter(db_query, *, category_ids=None, brand_ids=None, vendor_ids=None,
                 min_price=None, max_price=None, min_rating=None, in_stock=None,
                 q=None, attribute_name=None, attribute_value=None):
    if category_ids:
        db_query = db_query.where(Product.category_id.in_(category_ids))
    if brand_ids:
        db_query = db_query.where(Product.brand_id.in_(brand_ids))
    if vendor_ids:
        db_query = db_query.where(Product.id.in_(
            select(VendorProduct.product_id).where(
                VendorProduct.vendor_id.in_(vendor_ids), VendorProduct.status == 1)))
    if min_price is not None:
        db_query = db_query.where(Product.price >= min_price)
    if max_price is not None:
        db_query = db_query.where(Product.price <= max_price)
    if min_rating is not None:
        db_query = db_query.where(Product.rating >= min_rating)
    if in_stock is True:
        db_query = db_query.where(Product.stock > 0)
    elif in_stock is False:
        db_query = db_query.where(Product.stock <= 0)
    if q:
        like = f"%{q}%"
        db_query = db_query.where(or_(
            Product.name.like(like),
            Product.sku.like(like),
            Product.slug.like(like),
            Product.brand.has(Brand.name.like(like)),
            Product.category.has(Category.name.like(like)),
        ))
    if attribute_name and attribute_value:
        db_query = db_query.where(Product.id.in_(
            select(ProductVariant.product_id)
            .join(VariantAttribute, VariantAttribute.variant_id == ProductVariant.id)
            .where(VariantAttribute.attribute_name == attribute_name,
                   VariantAttribute.attribute_value == attribute_value)))
    return db_query


def _apply_sort(query, sort: str):
    col_name, direction = SORT_MAP.get(sort, ("created_at", "desc"))
    col = SORT_COLUMNS[col_name]
    if direction == "asc":
        return query.order_by(asc(col), asc(Product.id)), col, "asc"
    return query.order_by(desc(col), desc(Product.id)), col, "desc"


def _cursor_clause(sort: str, cursor: dict):
    col_name, direction = SORT_MAP.get(sort, ("created_at", "desc"))
    col = SORT_COLUMNS[col_name]
    try:
        raw = cursor.get("s")
        last_id = int(cursor["id"])
        if col_name in ("price", "rating"):
            v = Decimal(str(raw))
        elif col_name in ("review_count",):
            v = int(raw)
        elif col_name == "created_at":
            v = datetime.fromisoformat(str(raw))
        else:
            v = str(raw)
    except (InvalidOperation, ValueError, TypeError, KeyError):
        return None
    if direction == "desc":
        return or_(col < v, and_(col == v, Product.id < last_id))
    return or_(col > v, and_(col == v, Product.id > last_id))


def list_products(db: Session, *, page: int = 1, limit: int = 24, cursor: str | None = None,
                  sort: str = "newest", include_total: bool = True, use_cursor: bool = False, **filters):
    q = select(Product).where(Product.status == 1).options(
        selectinload(Product.descriptions),
        selectinload(Product.specifications),
    )
    q = _base_filter(q, **filters)

    if cursor or use_cursor:
        if cursor:
            data = decode_cursor(cursor)
            if data is None:
                return None, None, False, None
            clause = _cursor_clause(sort, data)
            if clause is not None:
                q = q.where(clause)
        q, _, _ = _apply_sort(q, sort)
        q = q.limit(limit + 1)
        rows = db.execute(q).scalars().unique().all()
        has_next = len(rows) > limit
        rows = rows[:limit]
        next_cursor = None
        if has_next and rows:
            last = rows[-1]
            col_name, _ = SORT_MAP.get(sort, ("created_at", "desc"))
            next_cursor = encode_cursor(last.id, getattr(last, col_name))
        return rows, None, has_next, next_cursor

    total = None
    if include_total:
        count_q = _base_filter(select(func.count(Product.id)).where(Product.status == 1), **filters)
        total = db.execute(count_q).scalar_one()
    q, _, _ = _apply_sort(q, sort)
    q = q.offset((page - 1) * limit).limit(limit)
    rows = db.execute(q).scalars().unique().all()
    has_next = page * limit < (total or 0) if total is not None else False
    return rows, total, has_next, None


def get_product(db: Session, product_id: int) -> Product | None:
    q = (select(Product)
         .where(Product.id == product_id)
         .options(
             selectinload(Product.images),
             selectinload(Product.prices),
             selectinload(Product.specifications),
             selectinload(Product.variants).selectinload(ProductVariant.attributes),
             selectinload(Product.descriptions),
             selectinload(Product.vendor_products).selectinload(VendorProduct.vendor),
         ))
    return db.execute(q).scalars().unique().first()


def get_primary_images(db: Session, product_ids: list[int]) -> dict[int, str | None]:
    if not product_ids:
        return {}
    q = (select(ProductImage.product_id, ProductImage.thumbnail_url, ProductImage.image_url)
         .where(ProductImage.product_id.in_(product_ids))
         .order_by(ProductImage.is_primary.desc(), ProductImage.sort_order.asc()))
    result: dict[int, str | None] = {}
    for pid, thumb, url in db.execute(q):
        if pid not in result:
            result[pid] = thumb or url
    return result


def create_product(db: Session, data: dict) -> Product:
    from app.models import Product as P
    p = P(**data)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def update_product(db: Session, product: Product, data: dict) -> Product:
    for key, value in data.items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product: Product) -> None:
    db.delete(product)
    db.commit()
