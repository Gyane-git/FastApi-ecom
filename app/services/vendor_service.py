from sqlalchemy.orm import Session

from app.repositories import vendor_repository, product_repository
from app.schemas.vendor import VendorOut
from app.services.product_service import _to_list_item


def list_vendors(db: Session, *, page, limit, q=None):
    rows, total = vendor_repository.list_vendors(db, page=page, limit=limit, q=q)
    counts = vendor_repository.product_counts(db, [v.id for v in rows])
    items = [_out(v, counts.get(v.id, 0)) for v in rows]
    return items, total


def get_vendor(db: Session, vendor_id: int):
    v = vendor_repository.get_vendor(db, vendor_id)
    if not v:
        return None
    counts = vendor_repository.product_counts(db, [v.id])
    return _out(v, counts.get(v.id, 0))


def _out(v, count) -> VendorOut:
    return VendorOut(id=v.id, name=v.name, slug=v.slug, email=v.email, phone=v.phone,
                     logo_url=v.logo_url, country_code=v.country_code, product_count=count)


def vendor_products(db: Session, vendor_id: int, *, page, limit):
    rows, total = vendor_repository.vendor_products(db, vendor_id, page=page, limit=limit)
    thumbs = product_repository.get_primary_images(db, [p.id for p in rows])
    return [_to_list_item(p, thumbs.get(p.id)) for p in rows], total
