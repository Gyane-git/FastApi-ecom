from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class BrandRef(BaseModel):
    id: int
    name: str


class CategoryRef(BaseModel):
    id: int
    name: str


class PriceRef(BaseModel):
    amount: Decimal
    currency: str = "NPR"


class DescriptionOut(BaseModel):
    language_code: str
    title: str
    short_description: str | None = None
    description: str | None = None


class SpecificationOut(BaseModel):
    specification_name: str
    specification_value: str
    language_code: str | None = None
    sort_order: int


class ProductListItem(BaseModel):
    id: int
    name: str
    slug: str
    sku: str
    brand: BrandRef | None = None
    category: CategoryRef | None = None
    price: PriceRef | None = None
    thumbnail: str | None = None
    rating: Decimal | None = None
    stock: int | None = None
    compare_price: Decimal | None = None
    short_description: str | None = None
    descriptions: list[DescriptionOut] = []
    specifications: list[SpecificationOut] = []


class ProductImageOut(BaseModel):
    id: int
    image_url: str
    thumbnail_url: str | None = None
    alt_text: str | None = None
    sort_order: int
    is_primary: bool


class ProductPriceOut(BaseModel):
    id: int
    country_code: str
    currency_code: str
    price: Decimal
    compare_price: Decimal | None = None
    is_active: bool


class VariantAttributeOut(BaseModel):
    attribute_name: str
    attribute_value: str


class ProductVariantOut(BaseModel):
    id: int
    sku: str
    barcode: str | None = None
    variant_name: str | None = None
    price: Decimal
    compare_price: Decimal | None = None
    stock: int
    status: int
    attributes: list[VariantAttributeOut] = []


class VendorRef(BaseModel):
    id: int
    name: str
    slug: str
    vendor_sku: str | None = None
    price: Decimal | None = None
    stock: int | None = None


class ReviewOut(BaseModel):
    id: int
    rating: int
    title: str | None = None
    review: str | None = None
    is_verified_purchase: bool
    created_at: datetime | None = None


class ReviewSummary(BaseModel):
    average_rating: float
    total_reviews: int
    distribution: dict[str, int]


class ProductDetail(BaseModel):
    id: int
    name: str
    slug: str
    sku: str
    barcode: str | None = None
    short_description: str | None = None
    description: str | None = None
    price: Decimal
    compare_price: Decimal | None = None
    stock: int
    rating: Decimal
    review_count: int
    weight: Decimal | None = None
    status: int
    created_at: datetime | None = None
    brand: BrandRef | None = None
    category: CategoryRef | None = None
    images: list[ProductImageOut] = []
    prices: list[ProductPriceOut] = []
    descriptions: list[DescriptionOut] = []
    specifications: list[SpecificationOut] = []
    variants: list[ProductVariantOut] = []
    vendors: list[VendorRef] = []
    review_summary: ReviewSummary | None = None
