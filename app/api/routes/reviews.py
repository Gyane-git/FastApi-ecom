from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models import Product
from app.repositories import review_repository
from app.schemas.product import ReviewOut
from app.utils.response import ok, err, paginated

router = APIRouter(tags=["Reviews"])


def _ensure_product(db: Session, product_id: int):
    if db.get(Product, product_id) is None:
        raise HTTPException(status_code=404, detail=err("Product not found"))


@router.get("/products/{product_id}/reviews", summary="Product reviews")
def list_reviews(product_id: int, page: int = Query(1, ge=1), limit: int = Query(24, ge=1, le=100), db: Session = Depends(get_db)):
    _ensure_product(db, product_id)
    rows, total = review_repository.list_reviews(db, product_id, page=page, limit=limit)
    items = [ReviewOut(id=r.id, rating=r.rating, title=r.title, review=r.review,
                       is_verified_purchase=bool(r.is_verified_purchase), created_at=r.created_at)
             for r in rows]
    return ok(paginated([i.model_dump(mode="json") for i in items], page, limit, total, page * limit < total))


@router.get("/products/{product_id}/reviews/summary", summary="Review summary")
def review_summary(product_id: int, db: Session = Depends(get_db)):
    _ensure_product(db, product_id)
    return ok(review_repository.review_summary(db, product_id))
