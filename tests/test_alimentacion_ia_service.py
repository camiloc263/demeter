from unittest.mock import patch

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from microservicio_alimentacion_ia.main import app
from microservicio_alimentacion_ia.db import models
from microservicio_alimentacion_ia.db.database import get_db

# Base de datos SQLite en memoria, aislada del archivo real del servicio:
# cada test corre contra un esquema limpio, sin tocar alimentacion_ia.db.
_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


def _override_get_db():
    db = _TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def _tabla_limpia():
    """Recrea el esquema antes de cada test para que no compartan datos entre sí."""
    models.Base.metadata.drop_all(bind=_engine)
    models.Base.metadata.create_all(bind=_engine)
    yield


def test_health():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "OK"
    assert response.json()["service"] == "Alimentación IA"


@patch("microservicio_alimentacion_ia.api.rutas_alimentacion.inventario_client.verificar_cerdo_en_corral")
def test_registrar_comida_con_rfid_valido(mock_verificar):
    """Cuando el Inventario confirma que el RFID pertenece al corral, se guarda el evento."""
    mock_verificar.return_value = None  # no lanza excepción -> el RFID es válido

    respuesta = client.post(
        "/alimentacion/registrar_comida",
        json={"id_cerdo_rfid": "C-001", "corral": "Corral A", "racion_servida_kg": 1.2},
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["id_cerdo_rfid"] == "C-001"
    assert cuerpo["corral"] == "Corral A"
    assert cuerpo["racion_servida_kg"] == 1.2
    assert "id" in cuerpo and "fecha_hora" in cuerpo
    mock_verificar.assert_called_once_with("Corral A", "C-001")


@patch("microservicio_alimentacion_ia.api.rutas_alimentacion.inventario_client.verificar_cerdo_en_corral")
def test_registrar_comida_con_rfid_invalido_no_se_guarda(mock_verificar):
    """Si el Inventario rechaza el RFID, la petición falla y no debe quedar nada guardado."""
    mock_verificar.side_effect = HTTPException(
        status_code=404, detail="El RFID 'NO-EXISTE' no corresponde a ningún cerdo registrado en el corral 'Corral A'."
    )

    respuesta = client.post(
        "/alimentacion/registrar_comida",
        json={"id_cerdo_rfid": "NO-EXISTE", "corral": "Corral A", "racion_servida_kg": 1.2},
    )

    assert respuesta.status_code == 404
    assert "no corresponde a ningún cerdo" in respuesta.json()["detail"]

    # Confirmamos que el rechazo ocurre ANTES de escribir en la base de datos.
    historial = client.get("/alimentacion/historial/NO-EXISTE")
    assert historial.json() == []


@patch("microservicio_alimentacion_ia.api.rutas_alimentacion.inventario_client.verificar_cerdo_en_corral")
def test_registrar_comida_con_inventario_caido(mock_verificar):
    """Si el servicio de Inventario no responde, se debe devolver 503, no un 500 genérico."""
    mock_verificar.side_effect = HTTPException(
        status_code=503, detail="El servicio de Inventario está fuera de línea. No se puede validar el RFID."
    )

    respuesta = client.post(
        "/alimentacion/registrar_comida",
        json={"id_cerdo_rfid": "C-001", "corral": "Corral A", "racion_servida_kg": 1.2},
    )

    assert respuesta.status_code == 503


@patch("microservicio_alimentacion_ia.api.rutas_alimentacion.inventario_client.verificar_cerdo_en_corral")
def test_historial_cerdo_ordena_mas_reciente_primero(mock_verificar):
    mock_verificar.return_value = None

    for racion in (1.0, 2.0, 3.0):
        client.post(
            "/alimentacion/registrar_comida",
            json={"id_cerdo_rfid": "C-002", "corral": "Corral B", "racion_servida_kg": racion},
        )

    historial = client.get("/alimentacion/historial/C-002")
    assert historial.status_code == 200
    raciones = [r["racion_servida_kg"] for r in historial.json()]
    assert raciones == [3.0, 2.0, 1.0]


def test_historial_cerdo_sin_registros_devuelve_lista_vacia():
    respuesta = client.get("/alimentacion/historial/SIN-REGISTROS")
    assert respuesta.status_code == 200
    assert respuesta.json() == []


@patch("microservicio_alimentacion_ia.api.rutas_alimentacion.modelo_nutricion")
def test_predecir_dieta_condiciones_normales(mock_modelo):
    mock_modelo.predict.return_value = [1.8]

    respuesta = client.post(
        "/alimentacion/predecir_dieta",
        json={"edad_dias": 60, "peso_actual_kg": 25, "temperatura_c": 22},
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["racion_recomendada_kg"] == 1.8
    assert cuerpo["costo_estimado_usd"] == 0.72
    assert cuerpo["analisis"] == "Condiciones óptimas para alimentación."


@patch("microservicio_alimentacion_ia.api.rutas_alimentacion.modelo_nutricion")
def test_predecir_dieta_alta_temperatura_agrega_advertencia(mock_modelo):
    mock_modelo.predict.return_value = [1.0]

    respuesta = client.post(
        "/alimentacion/predecir_dieta",
        json={"edad_dias": 60, "peso_actual_kg": 25, "temperatura_c": 32},
    )

    assert respuesta.status_code == 200
    assert "Alta temperatura" in respuesta.json()["analisis"]


@patch("microservicio_alimentacion_ia.api.rutas_alimentacion.modelo_nutricion", None)
def test_predecir_dieta_sin_modelo_disponible_devuelve_500():
    """Si modelo_nutricion.pkl no se pudo cargar (None), el endpoint debe fallar con 500 explícito."""
    respuesta = client.post(
        "/alimentacion/predecir_dieta",
        json={"edad_dias": 60, "peso_actual_kg": 25, "temperatura_c": 22},
    )
    assert respuesta.status_code == 500


def test_predecir_dieta_valida_rangos_de_entrada():
    """edad_dias, peso_actual_kg y temperatura_c tienen límites físicos (ver schemas/nutricion.py)."""
    respuesta = client.post(
        "/alimentacion/predecir_dieta",
        json={"edad_dias": 500, "peso_actual_kg": 25, "temperatura_c": 22},
    )
    assert respuesta.status_code == 422
