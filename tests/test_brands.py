def test_list_brands(client):
    r = client.get("/api/v1/brands?limit=5")
    assert r.status_code == 200


def test_brand_search(client):
    r = client.get("/api/v1/brands/search?q=brand")
    assert r.status_code == 200


def test_brand_detail(client):
    r = client.get("/api/v1/brands/1")
    assert r.status_code == 200


def test_brand_404(client):
    assert client.get("/api/v1/brands/999999999").status_code == 404


def test_brand_products(client):
    assert client.get("/api/v1/brands/1/products?limit=2").status_code == 200


def test_vendor_endpoints(client):
    assert client.get("/api/v1/vendors?limit=3").status_code == 200
    assert client.get("/api/v1/vendors/1").status_code == 200
    assert client.get("/api/v1/vendors/1/products?limit=2").status_code == 200
    assert client.get("/api/v1/vendors/search?q=store").status_code == 200
