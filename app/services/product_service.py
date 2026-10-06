from sqlalchemy.orm import Session

from app.models import Product
from app.models import ProductVariant, VendorProduct
from app.repositories import product_repository, review_repository
from app.schemas.product import (
    ProductListItem, BrandRef, CategoryRef, PriceRef, ProductDetail,
    ProductImageOut, ProductPriceOut, ProductVariantOut, VariantAttributeOut,
    VendorRef, SpecificationOut, ReviewSummary, DescriptionOut,
)


from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models import Product, Brand, Category, Vendor, VendorProduct
from app.schemas.product_filter import ProductFilters, FilterBrand, FilterCategory, PriceRange, VendorFilter


def get_filters(db: Session, *, category_id=None, brand_id=None, min_price=None, max_price=None, q=None) -> ProductFilters:
    conds = []
    if category_id:
        conds.append(Product.category_id == category_id)
    if brand_id:
        conds.append(Product.brand_id == brand_id)
    if min_price is not None:
        conds.append(Product.price >= min_price)
    if max_price is not None:
        conds.append(Product.price <= max_price)
    if q:
        conds.append(Product.name.like(f"%{q}%"))
    conds.append(Product.status == 1)

    brand_rows = db.execute(
        select(Brand.id, Brand.name, func.count(Product.id))
        .join(Product, Product.brand_id == Brand.id)
        .where(Brand.status == 1, *conds)
        .group_by(Brand.id, Brand.name).order_by(func.count(Product.id).desc()).limit(50)
    ).all()
    cat_rows = db.execute(
        select(Category.id, Category.name, func.count(Product.id))
        .join(Product, Product.category_id == Category.id)
        .where(Category.status == 1, *conds)
        .group_by(Category.id, Category.name).order_by(func.count(Product.id).desc()).limit(50)
    ).all()
    vendor_rows = db.execute(
        select(Vendor.id, Vendor.name, func.count(VendorProduct.id))
        .join(VendorProduct, VendorProduct.vendor_id == Vendor.id)
        .join(Product, Product.id == VendorProduct.product_id)
        .where(VendorProduct.status == 1, *conds)
        .group_by(Vendor.id, Vendor.name).order_by(func.count(VendorProduct.id).desc()).limit(50)
    ).all()
    price_min, price_max = db.execute(
        select(func.min(Product.price), func.max(Product.price))
        .where(*conds)
    ).one()

    return ProductFilters(
        brands=[FilterBrand(id=r[0], name=r[1], count=r[2]) for r in brand_rows],
        categories=[FilterCategory(id=r[0], name=r[1], count=r[2]) for r in cat_rows],
        vendors=[VendorFilter(id=r[0], name=r[1], count=r[2]) for r in vendor_rows],
        price=PriceRange(min=float(price_min) if price_min is not None else None,
                         max=float(price_max) if price_max is not None else None),
        ratings=[5, 4, 3, 2, 1],
    )


def _to_list_item(p: Product, thumbnail: str | None) -> ProductListItem:
    return ProductListItem(
        id=p.id, name=p.name, slug=p.slug, sku=p.sku,
        brand=BrandRef(id=p.brand.id, name=p.brand.name) if p.brand else None,
        category=CategoryRef(id=p.category.id, name=p.category.name) if p.category else None,
        price=PriceRef(amount=p.price, currency="NPR"),
        thumbnail=thumbnail,
        rating=p.rating,
        stock=p.stock,
        compare_price=p.compare_price,
        short_description=p.short_description,
        descriptions=[_desc_out(d) for d in sorted(p.descriptions or [], key=lambda x: x.id)],
        specifications=[_spec_out(s) for s in sorted(p.specifications or [], key=lambda x: x.sort_order)],
    )


def _spec_out(s) -> SpecificationOut:
    return SpecificationOut(specification_name=s.specification_name,
                            specification_value=s.specification_value,
                            language_code=s.language_code, sort_order=s.sort_order)


def _desc_out(d) -> DescriptionOut:
    return DescriptionOut(language_code=d.language_code, title=d.title,
                          short_description=d.short_description, description=d.description)


def list_products(db: Session, **kwargs):
    rows, total, has_next, next_cursor = product_repository.list_products(db, **kwargs)
    if rows is None:
        return None, None, False, None
    thumbs = product_repository.get_primary_images(db, [p.id for p in rows])
    items = [_to_list_item(p, thumbs.get(p.id)) for p in rows]
    return items, total, has_next, next_cursor


def get_product_detail(db: Session, product_id: int) -> ProductDetail | None:
    p = product_repository.get_product(db, product_id)
    if p is None:
        return None
    review_summary = ReviewSummary(**review_repository.review_summary(db, p.id))
    return ProductDetail(
        id=p.id, name=p.name, slug=p.slug, sku=p.sku, barcode=p.barcode,
        short_description=p.short_description, description=p.description,
        price=p.price, compare_price=p.compare_price, stock=p.stock,
        rating=p.rating, review_count=p.review_count, weight=p.weight,
        status=p.status, created_at=p.created_at,
        brand=BrandRef(id=p.brand.id, name=p.brand.name) if p.brand else None,
        category=CategoryRef(id=p.category.id, name=p.category.name) if p.category else None,
        images=[ProductImageOut(id=i.id, image_url=i.image_url, thumbnail_url=i.thumbnail_url,
                                alt_text=i.alt_text, sort_order=i.sort_order, is_primary=bool(i.is_primary))
                for i in sorted(p.images, key=lambda x: x.sort_order)],
        prices=[ProductPriceOut(id=pr.id, country_code=pr.country_code, currency_code=pr.currency_code,
                                price=pr.price, compare_price=pr.compare_price, is_active=bool(pr.is_active))
                for pr in p.prices if pr.is_active],
        specifications=[_spec_out(s) for s in sorted(p.specifications, key=lambda x: x.sort_order)],
        descriptions=[_desc_out(d) for d in sorted(p.descriptions, key=lambda x: x.id)],
        variants=[ProductVariantOut(id=v.id, sku=v.sku, barcode=v.barcode, variant_name=v.variant_name,
                                    price=v.price, compare_price=v.compare_price, stock=v.stock, status=v.status,
                                    attributes=[VariantAttributeOut(attribute_name=a.attribute_name, attribute_value=a.attribute_value)
                                                for a in v.attributes])
                  for v in p.variants],
        vendors=[VendorRef(id=vp.vendor.id, name=vp.vendor.name, slug=vp.vendor.slug,
                           vendor_sku=vp.vendor_sku, price=vp.price, stock=vp.stock)
                 for vp in p.vendor_products if vp.vendor and vp.status == 1 and vp.vendor.status == 1],
        review_summary=review_summary,
    )
