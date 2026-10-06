from pydantic import BaseModel


class FilterBrand(BaseModel):
    id: int
    name: str
    count: int


class FilterCategory(BaseModel):
    id: int
    name: str
    count: int


class PriceRange(BaseModel):
    min: float | None = None
    max: float | None = None


class VendorFilter(BaseModel):
    id: int
    name: str
    count: int


class ProductFilters(BaseModel):
    brands: list[FilterBrand] = []
    categories: list[FilterCategory] = []
    vendors: list[VendorFilter] = []
    price: PriceRange
    ratings: list[int] = []
