def test_list_categories(client):
    r = client.get("/api/v1/categories?limit=5")
    assert r.status_code == 200


def test_category_tree(client):
    r = client.get("/api/v1/categories/tree")
    assert r.status_code == 200
    assert isinstance(r.json()["data"], list)


def test_category_detail(client):
    r = client.get("/api/v1/categories/1")
    assert r.status_code == 200


def test_category_404(client):
    r = client.get("/api/v1/categories/999999999")
    assert r.status_code == 404


def test_category_children_and_breadcrumb(client):
    assert client.get("/api/v1/categories/1/children").status_code == 200
    assert client.get("/api/v1/categories/1/breadcrumb").status_code == 200
    assert client.get("/api/v1/categories/1/products?limit=2").status_code == 200
