from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models import Vendor, VendorProduct, Product
from sqlalchemy.orm import selectinload


def list_vendors(db: Session, *, page: int, limit: int, q: str | None = None):
    base = select(Vendor).where(Vendor.status == 1)
    if q:
        base = base.where(Vendor.name.like(f"%{q}%"))
    total = db.execute(select(func.count()).select_from(base.subquery())).scalar_one()
    rows = db.execute(base.order_by(Vendor.name).offset((page - 1) * limit).limit(limit)).scalars().all()
    return rows, total


def get_vendor(db: Session, vendor_id: int) -> Vendor | None:
    return db.get(Vendor, vendor_id)


def vendor_products(db: Session, vendor_id: int, *, page: int, limit: int):
    base = (select(Product)
            .options(selectinload(Product.descriptions), selectinload(Product.specifications))
            .join(VendorProduct, VendorProduct.product_id == Product.id)
            .where(VendorProduct.vendor_id == vendor_id, VendorProduct.status == 1, Product.status == 1))
    total = db.execute(select(func.count()).select_from(base.subquery())).scalar_one()
    rows = db.execute(base.order_by(Product.created_at.desc(), Product.id.desc()).offset((page - 1) * limit).limit(limit)).scalars().unique().all()
    return rows, total


def product_counts(db: Session, vendor_ids: list[int]) -> dict[int, int]:
    if not vendor_ids:
        return {}
    q = select(VendorProduct.vendor_id, func.count(VendorProduct.id)).where(VendorProduct.vendor_id.in_(vendor_ids), VendorProduct.status == 1).group_by(VendorProduct.vendor_id)
    return dict(db.execute(q).all())
