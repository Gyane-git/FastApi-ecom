from pydantic import BaseModel


class VendorOut(BaseModel):
    id: int
    name: str
    slug: str
    email: str | None = None
    phone: str | None = None
    logo_url: str | None = None
    country_code: str | None = None
    product_count: int | None = None
