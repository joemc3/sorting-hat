from fastapi.testclient import TestClient

from sorting_hat.main import app

client = TestClient(app)


def test_taxonomy_routes_registered():
    routes = [route.path for route in app.routes]
    assert "/api/v1/taxonomy/governance-groups" in routes
    assert "/api/v1/taxonomy/nodes" in routes
    assert "/api/v1/taxonomy/nodes/search" in routes
