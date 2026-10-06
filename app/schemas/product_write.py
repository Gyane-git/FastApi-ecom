from decimal import Decimal

from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    brand_id: int
    category_id: int
    sku: str = Field(..., max_length=100)
    barcode: str | None = Field(None, max_length=50)
    name: str = Field(..., max_length=500)
    slug: str | None = Field(None, max_length=600)
    short_description: str | None = None
    description: str | None = None
    price: Decimal = Field(default=0, ge=0)
    compare_price: Decimal | None = Field(None, ge=0)
    stock: int = Field(default=0, ge=0)
    weight: Decimal | None = Field(None, ge=0)
    status: int = Field(default=1, ge=0, le=1)


class ProductUpdate(BaseModel):
    brand_id: int | None = None
    category_id: int | None = None
    barcode: str | None = Field(None, max_length=50)
    name: str | None = Field(None, max_length=500)
    slug: str | None = Field(None, max_length=600)
    short_description: str | None = None
    description: str | None = None
    price: Decimal | None = Field(None, ge=0)
    compare_price: Decimal | None = Field(None, ge=0)
    stock: int | None = Field(None, ge=0)
    weight: Decimal | None = Field(None, ge=0)
    status: int | None = Field(None, ge=0, le=1)
