from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models import Brand, Product
from sqlalchemy.orm import selectinload


def list_brands(db: Session, *, page: int, limit: int, q: str | None = None):
    base = select(Brand).where(Brand.status == 1)
    if q:
        base = base.where(Brand.name.like(f"%{q}%"))
    total = db.execute(select(func.count()).select_from(base.subquery())).scalar_one()
    rows = db.execute(base.order_by(Brand.name).offset((page - 1) * limit).limit(limit)).scalars().all()
    return rows, total


def get_brand(db: Session, brand_id: int) -> Brand | None:
    return db.get(Brand, brand_id)


def list_brand_products(db: Session, brand_id: int, *, page: int, limit: int):
    base = select(Product).options(selectinload(Product.descriptions), selectinload(Product.specifications)).where(Product.brand_id == brand_id, Product.status == 1)
    total = db.execute(select(func.count()).select_from(base.subquery())).scalar_one()
    rows = db.execute(base.order_by(Product.created_at.desc(), Product.id.desc()).offset((page - 1) * limit).limit(limit)).scalars().unique().all()
    return rows, total


def product_counts(db: Session, brand_ids: list[int]) -> dict[int, int]:
    if not brand_ids:
        return {}
    q = select(Product.brand_id, func.count(Product.id)).where(Product.brand_id.in_(brand_ids)).group_by(Product.brand_id)
    return dict(db.execute(q).all())
