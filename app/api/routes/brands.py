from fastapi import APIRouter, Depends, Query, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.services import brand_service
from app.schemas.write import BrandUpdate
from app.utils.response import ok, err, paginated

router = APIRouter(prefix="/brands", tags=["Brands"])


@router.get("", summary="List brands")
def list_brands(page: int = Query(1, ge=1), limit: int = Query(24, ge=1, le=100), q: str | None = None, db: Session = Depends(get_db)):
    items, total = brand_service.list_brands(db, page=page, limit=limit, q=q)
    return ok(paginated([i.model_dump(mode="json") for i in items], page, limit, total, page * limit < total))


@router.get("/search", summary="Search brands")
def search_brands(q: str = Query(..., min_length=1), page: int = Query(1, ge=1), limit: int = Query(24, ge=1, le=100), db: Session = Depends(get_db)):
    items, total = brand_service.list_brands(db, page=page, limit=limit, q=q)
    return ok(paginated([i.model_dump(mode="json") for i in items], page, limit, total, page * limit < total))


@router.patch("/{brand_id}", summary="Update brand")
def update_brand(brand_id: int, payload: BrandUpdate, db: Session = Depends(get_db)):
    from app.models import Brand

    b = db.get(Brand, brand_id)
    if b is None:
        raise HTTPException(status_code=404, detail=err("Brand not found"))
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(b, key, value)
    db.commit()
    return ok(brand_service.get_brand(db, brand_id).model_dump(mode="json"), message="Brand updated")


@router.post("/{brand_id}/image", summary="Upload brand logo", status_code=201)
async def upload_brand_image(brand_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    from app.models import Brand
    from app.utils.upload import save_upload

    b = db.get(Brand, brand_id)
    if b is None:
        raise HTTPException(status_code=404, detail=err("Brand not found"))
    url = await save_upload(file)
    b.logo_url = url
    db.commit()
    return ok({"id": b.id, "logo_url": b.logo_url}, message="Brand image updated")


@router.get("/{brand_id}", summary="Brand detail")
def get_brand(brand_id: int, db: Session = Depends(get_db)):
    b = brand_service.get_brand(db, brand_id)
    if not b:
        raise HTTPException(status_code=404, detail=err("Brand not found"))
    return ok(b.model_dump(mode="json"))


@router.get("/{brand_id}/products", summary="Products by brand")
def brand_products(brand_id: int, page: int = Query(1, ge=1), limit: int = Query(24, ge=1, le=100), db: Session = Depends(get_db)):
    items, total = brand_service.brand_products(db, brand_id, page=page, limit=limit)
    return ok(paginated([i.model_dump(mode="json") for i in items], page, limit, total, page * limit < total))
