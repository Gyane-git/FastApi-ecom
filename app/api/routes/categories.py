from fastapi import APIRouter, Depends, Query, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.services import category_service
from app.schemas.write import CategoryUpdate
from app.utils.response import ok, err, paginated

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", summary="List categories")
def list_categories(page: int = Query(1, ge=1), limit: int = Query(50, ge=1, le=200),
                    parent_id: int | None = None, q: str | None = None, db: Session = Depends(get_db)):
    items, total = category_service.list_categories(db, page=page, limit=limit, parent_id=parent_id, q=q)
    return ok(paginated([i.model_dump(mode="json") for i in items], page, limit, total, page * limit < total))


@router.get("/tree", summary="Full category tree")
def tree(db: Session = Depends(get_db)):
    nodes = category_service.get_tree(db)
    return ok([n.model_dump(mode="json") for n in nodes])


@router.patch("/{category_id}", summary="Update category")
def update_category(category_id: int, payload: CategoryUpdate, db: Session = Depends(get_db)):
    from app.models import Category

    c = db.get(Category, category_id)
    if c is None:
        raise HTTPException(status_code=404, detail=err("Category not found"))
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(c, key, value)
    db.commit()
    return ok(category_service.get_category(db, category_id).model_dump(mode="json"), message="Category updated")


@router.post("/{category_id}/image", summary="Upload category image", status_code=201)
async def upload_category_image(category_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    from app.models import Category
    from app.utils.upload import save_upload

    c = db.get(Category, category_id)
    if c is None:
        raise HTTPException(status_code=404, detail=err("Category not found"))
    url = await save_upload(file)
    c.image_url = url
    db.commit()
    return ok({"id": c.id, "image_url": c.image_url}, message="Category image updated")


@router.get("/{category_id}", summary="Category detail")
def get_category(category_id: int, db: Session = Depends(get_db)):
    c = category_service.get_category(db, category_id)
    if not c:
        raise HTTPException(status_code=404, detail=err("Category not found"))
    return ok(c.model_dump(mode="json"))


@router.get("/{category_id}/children", summary="Child categories")
def children(category_id: int, db: Session = Depends(get_db)):
    return ok([c.model_dump(mode="json") for c in category_service.children(db, category_id)])


@router.get("/{category_id}/breadcrumb", summary="Category breadcrumb")
def breadcrumb(category_id: int, db: Session = Depends(get_db)):
    return ok([c.model_dump(mode="json") for c in category_service.breadcrumb(db, category_id)])


@router.get("/{category_id}/products", summary="Products in category")
def category_products(category_id: int, page: int = Query(1, ge=1), limit: int = Query(24, ge=1, le=100), db: Session = Depends(get_db)):
    items, total = category_service.category_products(db, category_id, page=page, limit=limit)
    return ok(paginated([i.model_dump(mode="json") for i in items], page, limit, total, page * limit < total))
