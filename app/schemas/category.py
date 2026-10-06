from pydantic import BaseModel


class CategoryOut(BaseModel):
    id: int
    parent_id: int | None = None
    name: str
    slug: str
    description: str | None = None
    image_url: str | None = None
    level: int
    product_count: int | None = None


class CategoryTreeNode(BaseModel):
    id: int
    parent_id: int | None = None
    name: str
    slug: str
    image_url: str | None = None
    level: int
    children: list["CategoryTreeNode"] = []
