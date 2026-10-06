from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models import ProductReview


def list_reviews(db: Session, product_id: int, *, page: int, limit: int):
    base = select(ProductReview).where(ProductReview.product_id == product_id, ProductReview.status == 1)
    total = db.execute(select(func.count()).select_from(base.subquery())).scalar_one()
    rows = db.execute(base.order_by(ProductReview.created_at.desc(), ProductReview.id.desc()).offset((page - 1) * limit).limit(limit)).scalars().all()
    return rows, total


def review_summary(db: Session, product_id: int) -> dict:
    avg, total = db.execute(
        select(func.avg(ProductReview.rating), func.count(ProductReview.id))
        .where(ProductReview.product_id == product_id, ProductReview.status == 1)
    ).one()
    dist_rows = db.execute(
        select(ProductReview.rating, func.count(ProductReview.id))
        .where(ProductReview.product_id == product_id, ProductReview.status == 1)
        .group_by(ProductReview.rating)
    ).all()
    distribution = {str(r): 0 for r in (5, 4, 3, 2, 1)}
    for rating, count in dist_rows:
        distribution[str(rating)] = count
    return {
        "average_rating": round(float(avg or 0), 2),
        "total_reviews": total or 0,
        "distribution": distribution,
    }
