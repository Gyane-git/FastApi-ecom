# Ecommerce API

Professional, scalable REST API built with FastAPI + SQLAlchemy 2.x + MySQL (MariaDB), designed for a large catalog (~200k products, ~10k brands, ~5k categories) and ready for a Next.js frontend or mobile clients.

## Architecture

Layered, read-only-first architecture:

- `app/api/routes/` — HTTP layer only (validation, envelope, status codes)
- `app/services/` — business logic / orchestration
- `app/repositories/` — all SQL lives here (SQLAlchemy 2.x `select()` style)
- `app/models/` — ORM models mirroring the real `ecomTest_db` schema
- `app/schemas/` — Pydantic v2 response models
- `app/core/` — config (pydantic-settings), engine/session, logging
- `app/utils/` — pagination (offset + keyset cursor), response envelope

The existing database is treated as the source of truth. **No schema changes are applied.** See `INDEX_AUDIT.md` for recommended (non-applied) index changes.

## Requirements

- Python 3.11+
- MySQL 8+ / MariaDB 10.4+

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # edit credentials
```

## Run

```bash
uvicorn app.main:app --reload --port 8000
# or
python run.py
```

Swagger UI: http://localhost:8000/docs — ReDoc: http://localhost:8000/redoc

## Tests

```bash
pytest tests -q
```

Tests are read-only against the configured database. Never point `DATABASE_URL` at production data you care about without review.

## Performance test

```bash
uvicorn app.main:app --port 8000
python scripts/perf_test.py
```

Measured locally (MariaDB 10.4, InnoDB, warm cache):

| Endpoint | Avg response |
|---|---|
| GET /products?limit=24 | ~200ms |
| GET /products?limit=24&use_cursor=true | ~172ms |
| GET /products/search?q=camera | ~590ms (LIKE scan) |
| GET /products/1 (detail) | ~17ms |
| GET /products?category_id=10 | ~9ms |
| GET /products?brand_id=25 | ~35ms |
| GET /products?min_price&max_price | ~49ms |

## API overview (`/api/v1`)

### Products
- `GET /products` — filters: `category_id`, `brand_id`, `vendor_id`, `category_ids`, `brand_ids`, `min_price`, `max_price`, `min_rating`, `in_stock`, `q`, `sort`, `attribute_name`/`attribute_value`, `page`/`limit` or `use_cursor=true&cursor=...`
- `GET /products/search?q=...`
- `GET /products/featured` / `GET /products/latest`
- `GET /products/filters` — faceted filter counts
- `GET /products/{id}` — full detail (images, prices, specs, variants, vendors, review summary)
- `GET /products/{id}/related|variants|images|vendors|reviews|reviews/summary`

### Brands / Categories / Vendors
- `GET /brands`, `/brands/{id}`, `/brands/{id}/products`, `/brands/search`
- `GET /categories`, `/categories/{id}`, `/categories/tree`, `/categories/{id}/children`, `/categories/{id}/breadcrumb`, `/categories/{id}/products`
- `GET /vendors`, `/vendors/{id}`, `/vendors/{id}/products`, `/vendors/search`

### Health
- `GET /health`, `GET /health/db`

## Pagination strategy

Two modes, both supported:

1. **Offset** (`page`, `limit`) — fine for shallow pages.
2. **Keyset/cursor** (`use_cursor=true&cursor=...`) — stable, index-friendly deep browsing; returns `next_cursor`.

## Response envelope

```json
{ "success": true, "data": { ... }, "message": null }
```

Errors:

```json
{ "success": false, "data": null, "message": "Product not found" }
```

## Security / production notes

- All SQL goes through SQLAlchemy parameterized queries (no string-built SQL ORDER BY; sorting is whitelisted).
- CORS origins come from `CORS_ORIGINS` env var.
- No stack traces, credentials, or internal SQL are exposed; a global exception handler reshapes errors.
- Structured request logging (method, path, status, duration) — no secrets logged.
- Connection pooling: `pool_pre_ping`, `pool_recycle`, bounded `pool_size` + `max_overflow`.
- Architecture is cache-ready (service boundaries); add Redis later for category tree, filters, popular brands, product detail.
