from sqlalchemy.orm import Session

from app.services import product_service


def search(db: Session, q: str, *, page: int = 1, limit: int = 24, sort: str = "newest", cursor: str | None = None, use_cursor: bool = False):
    return product_service.list_products(
        db, page=page, limit=limit, cursor=cursor, sort=sort, q=q, include_total=cursor is None and not use_cursor, use_cursor=use_cursor)
