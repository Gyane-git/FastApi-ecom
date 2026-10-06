from typing import Any


def ok(data: Any = None, message: str | None = None) -> dict:
    return {"success": True, "data": data, "message": message}


def err(message: str) -> dict:
    return {"success": False, "data": None, "message": message}


def paginated(items: list, page: int | None, limit: int, total: int | None, has_next: bool, next_cursor: str | None = None) -> dict:
    pagination: dict[str, Any] = {"limit": limit, "has_next": has_next}
    if page is not None:
        pagination["page"] = page
    if total is not None:
        pagination["total"] = total
    if next_cursor is not None:
        pagination["next_cursor"] = next_cursor
    return {"items": items, "pagination": pagination}
