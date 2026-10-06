from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.services import vendor_service
from app.schemas.write import VendorUpdate
from app.utils.response import ok, err, paginated

router = APIRouter(prefix="/vendors", tags=["Vendors"])


@router.get("", summary="List vendors")
def list_vendors(page: int = Query(1, ge=1), limit: int = Query(24, ge=1, le=100), q: str | None = None, db: Session = Depends(get_db)):
    items, total = vendor_service.list_vendors(db, page=page, limit=limit, q=q)
    return ok(paginated([i.model_dump(mode="json") for i in items], page, limit, total, page * limit < total))


@router.get("/search", summary="Search vendors")
def search_vendors(q: str = Query(..., min_length=1), page: int = Query(1, ge=1), limit: int = Query(24, ge=1, le=100), db: Session = Depends(get_db)):
    items, total = vendor_service.list_vendors(db, page=page, limit=limit, q=q)
    return ok(paginated([i.model_dump(mode="json") for i in items], page, limit, total, page * limit < total))


@router.patch("/{vendor_id}", summary="Update vendor")
def update_vendor(vendor_id: int, payload: VendorUpdate, db: Session = Depends(get_db)):
    from app.models import Vendor

    v = db.get(Vendor, vendor_id)
    if v is None:
        raise HTTPException(status_code=404, detail=err("Vendor not found"))
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(v, key, value)
    db.commit()
    return ok(vendor_service.get_vendor(db, vendor_id).model_dump(mode="json"), message="Vendor updated")


@router.get("/{vendor_id}", summary="Vendor detail")
def get_vendor(vendor_id: int, db: Session = Depends(get_db)):
    v = vendor_service.get_vendor(db, vendor_id)
    if not v:
        raise HTTPException(status_code=404, detail=err("Vendor not found"))
    return ok(v.model_dump(mode="json"))


@router.get("/{vendor_id}/products", summary="Products by vendor")
def vendor_products(vendor_id: int, page: int = Query(1, ge=1), limit: int = Query(24, ge=1, le=100), db: Session = Depends(get_db)):
    items, total = vendor_service.vendor_products(db, vendor_id, page=page, limit=limit)
    return ok(paginated([i.model_dump(mode="json") for i in items], page, limit, total, page * limit < total))
