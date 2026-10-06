from sqlalchemy.orm import Session

from app.repositories import category_repository, product_repository
from app.schemas.category import CategoryOut, CategoryTreeNode
from app.services.product_service import _to_list_item


def list_categories(db: Session, *, page, limit, parent_id=None, q=None):
    rows, total = category_repository.list_categories(db, page=page, limit=limit, parent_id=parent_id, q=q)
    return [_out(c) for c in rows], total


def get_category(db: Session, category_id: int):
    c = category_repository.get_category(db, category_id)
    return _out(c) if c else None


def _out(c) -> CategoryOut:
    return CategoryOut(id=c.id, parent_id=c.parent_id, name=c.name, slug=c.slug,
                       description=c.description, image_url=c.image_url, level=c.level)


def get_tree(db: Session) -> list[CategoryTreeNode]:
    rows = category_repository.get_all_active(db)
    nodes: dict[int, CategoryTreeNode] = {}
    roots: list[CategoryTreeNode] = []
    for c in rows:
        nodes[c.id] = CategoryTreeNode(id=c.id, parent_id=c.parent_id, name=c.name, slug=c.slug,
                                       image_url=c.image_url, level=c.level, children=[])
    for c in rows:
        node = nodes[c.id]
        if c.parent_id and c.parent_id in nodes:
            nodes[c.parent_id].children.append(node)
        else:
            roots.append(node)
    return roots


def children(db: Session, category_id: int):
    return [_out(c) for c in category_repository.get_children(db, category_id)]


def breadcrumb(db: Session, category_id: int):
    return [_out(c) for c in category_repository.breadcrumb(db, category_id)]


def category_products(db: Session, category_id: int, *, page, limit):
    rows, total = category_repository.category_products(db, category_id, page=page, limit=limit)
    thumbs = product_repository.get_primary_images(db, [p.id for p in rows])
    return [_to_list_item(p, thumbs.get(p.id)) for p in rows], total
