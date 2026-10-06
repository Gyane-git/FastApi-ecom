from fastapi import APIRouter, Depends, Query, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.services import product_service, search_service
from app.utils.response import ok, err, paginated
from app.utils.filters import SortOption
from app.schemas.product_write import ProductCreate, ProductUpdate

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", summary="List products with filters, sorting and pagination")
def list_products(
    page: int = Query(1, ge=1),
    limit: int = Query(24, ge=1, le=100),
    cursor: str | None = Query(None, description="Keyset cursor for scalable pagination"),
    use_cursor: bool = Query(False, description="Enable keyset/cursor pagination instead of offset"),
    category_id: int | None = None,
    brand_id: int | None = None,
    vendor_id: int | None = None,
    category_ids: str | None = Query(None, description="Comma-separated category IDs"),
    brand_ids: str | None = Query(None, description="Comma-separated brand IDs"),
    min_price: float | None = Query(None, ge=0),
    max_price: float | None = Query(None, ge=0),
    min_rating: float | None = Query(None, ge=0, le=5),
    in_stock: bool | None = None,
    q: str | None = Query(None, max_length=200),
    sort: SortOption = "newest",
    attribute_name: str | None = None,
    attribute_value: str | None = None,
    db: Session = Depends(get_db),
):
    cat_ids = [int(x) for x in category_ids.split(",") if x.strip().isdigit()] if category_ids else []
    if category_id:
        cat_ids.append(category_id)
    b_ids = [int(x) for x in brand_ids.split(",") if x.strip().isdigit()] if brand_ids else []
    if brand_id:
        b_ids.append(brand_id)
    v_ids = [vendor_id] if vendor_id else None

    items, total, has_next, next_cursor = product_service.list_products(
        db, page=page, limit=limit, cursor=cursor, sort=sort, include_total=True, use_cursor=use_cursor,
        category_ids=cat_ids or None, brand_ids=b_ids or None, vendor_ids=v_ids,
        min_price=min_price, max_price=max_price, min_rating=min_rating,
        in_stock=in_stock, q=q, attribute_name=attribute_name, attribute_value=attribute_value,
    )
    if items is None:
        return err("Invalid cursor")
    return ok(paginated([i.model_dump(mode="json") for i in items], page if not (cursor or use_cursor) else None, limit, total, has_next, next_cursor))


@router.get("/search", summary="Search products")
def search(q: str = Query(..., min_length=1, max_length=200), page: int = Query(1, ge=1),
           limit: int = Query(24, ge=1, le=100), cursor: str | None = None, use_cursor: bool = False, sort: SortOption = "newest",
           db: Session = Depends(get_db)):
    items, total, has_next, next_cursor = search_service.search(db, q, page=page, limit=limit, sort=sort, cursor=cursor, use_cursor=use_cursor)
    if items is None:
        return err("Invalid cursor")
    return ok(paginated([i.model_dump(mode="json") for i in items], page if not (cursor or use_cursor) else None, limit, total, has_next, next_cursor))


@router.get("/featured", summary="Featured products (top rated)")
def featured(limit: int = Query(24, ge=1, le=100), page: int = Query(1, ge=1), db: Session = Depends(get_db)):
    items, total, has_next, _ = product_service.list_products(db, page=page, limit=limit, sort="rating", include_total=True, min_rating=4.0)
    return ok(paginated([i.model_dump(mode="json") for i in items], page, limit, total, has_next))


@router.get("/latest", summary="Latest products")
def latest(limit: int = Query(24, ge=1, le=100), page: int = Query(1, ge=1), db: Session = Depends(get_db)):
    items, total, has_next, _ = product_service.list_products(db, page=page, limit=limit, sort="newest", include_total=True)
    return ok(paginated([i.model_dump(mode="json") for i in items], page, limit, total, has_next))


@router.get("/filters", summary="Available filters/facets")
def filters(category_id: int | None = None, brand_id: int | None = None,
            min_price: float | None = None, max_price: float | None = None, q: str | None = None,
            db: Session = Depends(get_db)):
    return ok(product_service.get_filters(db, category_id=category_id, brand_id=brand_id,
                                          min_price=min_price, max_price=max_price, q=q).model_dump(mode="json"))


@router.post("", summary="Create product", status_code=201)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    from app.repositories import product_repository
    from sqlalchemy import select
    from app.models import Brand, Category

    if db.get(Brand, payload.brand_id) is None:
        raise HTTPException(status_code=400, detail=err("Invalid brand_id"))
    if db.get(Category, payload.category_id) is None:
        raise HTTPException(status_code=400, detail=err("Invalid category_id"))
    data = payload.model_dump()
    if not data.get("slug"):
        data["slug"] = payload.name.lower().replace(" ", "-")[:590] + f"-{payload.sku.lower()}"
    try:
        p = product_repository.create_product(db, data)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=409, detail=err("SKU, slug or barcode already exists"))
    return ok(product_service.get_product_detail(db, p.id).model_dump(mode="json"), message="Product created")


@router.patch("/{product_id}", summary="Update product")
def update_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db)):
    from app.repositories import product_repository
    from app.models import Product

    p = db.get(Product, product_id)
    if p is None:
        raise HTTPException(status_code=404, detail=err("Product not found"))
    data = payload.model_dump(exclude_unset=True)
    if not data:
        return ok(product_service.get_product_detail(db, product_id).model_dump(mode="json"))
    try:
        product_repository.update_product(db, p, data)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=409, detail=err("Conflict while updating product"))
    return ok(product_service.get_product_detail(db, product_id).model_dump(mode="json"), message="Product updated")


@router.delete("/{product_id}", summary="Delete product")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    from app.repositories import product_repository
    from app.models import Product

    p = db.get(Product, product_id)
    if p is None:
        raise HTTPException(status_code=404, detail=err("Product not found"))
    product_repository.delete_product(db, p)
    return ok(message="Product deleted")


@router.get("/{product_id}", summary="Product detail")
def get_product(product_id: int, db: Session = Depends(get_db)):
    detail = product_service.get_product_detail(db, product_id)
    if detail is None:
        raise HTTPException(status_code=404, detail=err("Product not found"))
    return ok(detail.model_dump(mode="json"))


@router.get("/{product_id}/related", summary="Related products (same category)")
def related(product_id: int, limit: int = Query(12, ge=1, le=50), db: Session = Depends(get_db)):
    p = product_service.get_product_detail(db, product_id)
    if p is None:
        raise HTTPException(status_code=404, detail=err("Product not found"))
    items, total, has_next, _ = product_service.list_products(
        db, page=1, limit=limit + 1, sort="rating", include_total=False,
        category_ids=[p.category.id] if p.category else None)
    filtered = [i for i in items if i.id != product_id][:limit]
    return ok({"items": [i.model_dump(mode="json") for i in filtered]})


@router.post("/{product_id}/images", summary="Upload product image", status_code=201)
async def upload_product_image(product_id: int, file: UploadFile = File(...), is_primary: bool = False, alt_text: str | None = None, db: Session = Depends(get_db)):
    from app.models import Product, ProductImage
    from app.utils.upload import save_upload

    if db.get(Product, product_id) is None:
        raise HTTPException(status_code=404, detail=err("Product not found"))
    url = await save_upload(file)
    img = ProductImage(product_id=product_id, image_url=url, thumbnail_url=url, alt_text=alt_text, is_primary=1 if is_primary else 0, sort_order=0)
    db.add(img)
    db.commit()
    db.refresh(img)
    return ok({"id": img.id, "image_url": img.image_url}, message="Image uploaded")


@router.get("/{product_id}/variants", summary="Product variants")
def variants(product_id: int, db: Session = Depends(get_db)):
    p = product_service.get_product_detail(db, product_id)
    if p is None:
        raise HTTPException(status_code=404, detail=err("Product not found"))
    return ok([v.model_dump(mode="json") for v in p.variants])


@router.get("/{product_id}/images", summary="Product images")
def images(product_id: int, db: Session = Depends(get_db)):
    p = product_service.get_product_detail(db, product_id)
    if p is None:
        raise HTTPException(status_code=404, detail=err("Product not found"))
    return ok([i.model_dump(mode="json") for i in p.images])


@router.get("/{product_id}/vendors", summary="Product vendors")
def vendors(product_id: int, db: Session = Depends(get_db)):
    p = product_service.get_product_detail(db, product_id)
    if p is None:
        raise HTTPException(status_code=404, detail=err("Product not found"))
    return ok([v.model_dump(mode="json") for v in p.vendors])
