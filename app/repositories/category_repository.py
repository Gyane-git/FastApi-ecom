from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models import Category, Product
from sqlalchemy.orm import selectinload


def list_categories(db: Session, *, page: int, limit: int, parent_id=None, q=None):
    base = select(Category).where(Category.status == 1)
    if parent_id is not None:
        base = base.where(Category.parent_id == parent_id)
    if q:
        base = base.where(Category.name.like(f"%{q}%"))
    total = db.execute(select(func.count()).select_from(base.subquery())).scalar_one()
    rows = db.execute(base.order_by(Category.name).offset((page - 1) * limit).limit(limit)).scalars().all()
    return rows, total


def get_category(db: Session, category_id: int) -> Category | None:
    return db.get(Category, category_id)


def get_all_active(db: Session) -> list[Category]:
    return db.execute(select(Category).where(Category.status == 1).order_by(Category.id)).scalars().all()


def get_children(db: Session, category_id: int) -> list[Category]:
    return db.execute(select(Category).where(Category.parent_id == category_id, Category.status == 1).order_by(Category.name)).scalars().all()


def breadcrumb(db: Session, category_id: int) -> list[Category]:
    chain = []
    current = db.get(Category, category_id)
    depth = 0
    while current is not None and depth < 20:
        chain.append(current)
        current = db.get(Category, current.parent_id) if current.parent_id else None
        depth += 1
    return list(reversed(chain))


def category_products(db: Session, category_id: int, *, page: int, limit: int):
    base = select(Product).options(selectinload(Product.descriptions), selectinload(Product.specifications)).where(Product.category_id == category_id, Product.status == 1)
    total = db.execute(select(func.count()).select_from(base.subquery())).scalar_one()
    rows = db.execute(base.order_by(Product.created_at.desc(), Product.id.desc()).offset((page - 1) * limit).limit(limit)).scalars().unique().all()
    return rows, total
