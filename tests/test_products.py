import pytest


def test_list_products(client):
    r = client.get("/api/v1/products?limit=5")
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert len(body["data"]["items"]) == 5
    assert body["data"]["pagination"]["limit"] == 5


def test_product_detail(client):
    r = client.get("/api/v1/products/1")
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["id"] == 1
    assert "brand" in data and "images" in data


def test_product_not_found(client):
    r = client.get("/api/v1/products/999999999")
    assert r.status_code == 404
    assert r.json()["success"] is False


def test_search(client):
    r = client.get("/api/v1/products/search?q=camera")
    assert r.status_code == 200
    assert r.json()["success"] is True


def test_category_filter(client):
    r = client.get("/api/v1/products?category_id=10&limit=3")
    assert r.status_code == 200


def test_brand_filter(client):
    r = client.get("/api/v1/products?brand_id=25&limit=3")
    assert r.status_code == 200


def test_price_filter(client):
    r = client.get("/api/v1/products?min_price=100&max_price=5000&limit=3")
    assert r.status_code == 200
    for item in r.json()["data"]["items"]:
        assert 100 <= float(item["price"]["amount"]) <= 5000


@pytest.mark.parametrize("sort", ["newest", "oldest", "price_asc", "price_desc", "rating", "popularity", "name_asc", "name_desc"])
def test_sorting(client, sort):
    r = client.get(f"/api/v1/products?limit=3&sort={sort}")
    assert r.status_code == 200


def test_cursor_pagination(client):
    r1 = client.get("/api/v1/products?limit=3&sort=price_desc&use_cursor=true")
    assert r1.status_code == 200
    nc = r1.json()["data"]["pagination"]["next_cursor"]
    r2 = client.get(f"/api/v1/products?limit=3&sort=price_desc&use_cursor=true&cursor={nc}")
    assert r2.status_code == 200
    ids1 = {i["id"] for i in r1.json()["data"]["items"]}
    ids2 = {i["id"] for i in r2.json()["data"]["items"]}
    assert not (ids1 & ids2)
