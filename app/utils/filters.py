from typing import Annotated, Literal

from fastapi import Query

SortOption = Literal["newest", "oldest", "price_asc", "price_desc", "rating", "popularity", "name_asc", "name_desc"]

SORT_COLUMNS = {
    "newest": "created_at_desc",
    "oldest": "created_at_asc",
    "price_asc": "price_asc",
    "price_desc": "price_desc",
    "rating": "rating_desc",
    "popularity": "review_count_desc",
    "name_asc": "name_asc",
    "name_desc": "name_desc",
}

CommonQuery = Annotated[int | None, Query(description="Category ID")]
