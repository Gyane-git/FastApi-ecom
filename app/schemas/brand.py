from pydantic import BaseModel


class BrandOut(BaseModel):
    id: int
    name: str
    slug: str
    logo_url: str | None = None
    description: str | None = None
    product_count: int | None = None
