from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_predecir():
    payload = {
        "temperatura_c": 25.0,
        "humedad_pct": 60.0,
        "peso_promedio_kg": 50.0
    }
    response = client.post("/predecir", json=payload)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    # Basic structure checks
    assert "estado_codigo" in data
    assert "mensaje" in data
    assert "certeza_porcentaje" in data
    assert "analisis_modelo" in data
    # Ensure the message is one of the defined options
    assert data["mensaje"] in ["ÓPTIMO - Los cerdos están confortables.",
                               "ALERTA - Posible inicio de estrés calórico.",
                               "PELIGRO - Riesgo inminente de infarto."]
    # Certeza should be a number between 0 and 100
    assert isinstance(data["certeza_porcentaje"], (int, float))
    assert 0 <= data["certeza_porcentaje"] <= 100

if __name__ == "__main__":
    test_predecir()
    print("Test completado satisfactoriamente.")