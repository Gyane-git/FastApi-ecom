from pydantic import BaseModel, Field


class BrandUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: int | None = Field(None, ge=0, le=1)


class CategoryUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: int | None = Field(None, ge=0, le=1)


class VendorUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    status: int | None = Field(None, ge=0, le=1)
