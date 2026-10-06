from sqlalchemy.orm import Session

from app.repositories import brand_repository
from app.schemas.brand import BrandOut


def list_brands(db: Session, *, page, limit, q=None):
    rows, total = brand_repository.list_brands(db, page=page, limit=limit, q=q)
    counts = brand_repository.product_counts(db, [b.id for b in rows])
    items = [BrandOut(id=b.id, name=b.name, slug=b.slug, logo_url=b.logo_url,
                      description=b.description, product_count=counts.get(b.id, 0)) for b in rows]
    return items, total


def get_brand(db, brand_id):
    b = brand_repository.get_brand(db, brand_id)
    if not b:
        return None
    counts = brand_repository.product_counts(db, [b.id])
    return BrandOut(id=b.id, name=b.name, slug=b.slug, logo_url=b.logo_url,
                    description=b.description, product_count=counts.get(b.id, 0))


def brand_products(db, brand_id, *, page, limit):
    rows, total = brand_repository.list_brand_products(db, brand_id, page=page, limit=limit)
    from app.services.product_service import _to_list_item
    from app.repositories import product_repository
    thumbs = product_repository.get_primary_images(db, [p.id for p in rows])
    return [_to_list_item(p, thumbs.get(p.id)) for p in rows], total
