from fastapi.testclient import TestClient

from sorting_hat.main import app

client = TestClient(app)


def test_classification_routes_registered():
    routes = [route.path for route in app.routes]
    assert "/api/v1/classify" in routes
    assert "/api/v1/classify/{classification_id}" in routes
