import pytest
from fastapi.testclient import TestClient
from microservicio_inventario.main import app

client = TestClient(app)

def test_health():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "OK"
    assert response.json()["service"] == "Inventario"