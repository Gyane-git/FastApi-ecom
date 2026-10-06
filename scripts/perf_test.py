"""Simple performance smoke script. Run with the API server up:
    uvicorn app.main:app --port 8000
    python scripts/perf_test.py
"""
import time

import httpx

BASE = "http://127.0.0.1:8000"

CASES = [
    ("product list", "/api/v1/products?limit=24"),
    ("product list (cursor)", "/api/v1/products?limit=24&use_cursor=true"),
    ("product search", "/api/v1/products/search?q=camera"),
    ("product detail", "/api/v1/products/1"),
    ("category filter", "/api/v1/products?category_id=10&limit=24"),
    ("brand filter", "/api/v1/products?brand_id=25&limit=24"),
    ("price filter", "/api/v1/products?min_price=100&max_price=5000&limit=24"),
]


def main():
    with httpx.Client(base_url=BASE, timeout=30) as c:
        for name, url in CASES:
            times = []
            for _ in range(3):
                t0 = time.perf_counter()
                r = c.get(url)
                times.append((time.perf_counter() - t0) * 1000)
                assert r.status_code == 200, (url, r.status_code)
            print(f"{name:28s} avg={sum(times)/len(times):8.1f}ms  runs={[f'{t:.0f}' for t in times]}")


if __name__ == "__main__":
    main()
