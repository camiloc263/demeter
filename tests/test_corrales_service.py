import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from microservicio_corrales.main import app
from microservicio_corrales.db.models import Base, get_db

from conftest import header_auth

# Base de datos SQLite en memoria, aislada del archivo real del servicio.
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
    Base.metadata.drop_all(bind=_engine)
    Base.metadata.create_all(bind=_engine)
    yield


_CORRAL_VALIDO = {
    "nombre": "Corral Test",
    "capacidad_maxima": 10,
    "ancho_m": 5,
    "largo_m": 4,
    "etapa": "Engorde",
}


def test_health():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "OK"
    assert response.json()["service"] == "Corrales"


def test_crear_corral_sin_token_devuelve_401():
    respuesta = client.post("/corrales/", json=_CORRAL_VALIDO)
    assert respuesta.status_code == 401


def test_crear_corral_con_token_valido_devuelve_200():
    respuesta = client.post("/corrales/", json=_CORRAL_VALIDO, headers=header_auth())
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["nombre"] == "Corral Test"
    assert cuerpo["area_m2"] == 20.0


def test_leer_corrales_no_requiere_token():
    """Las lecturas quedan abiertas: otros servicios las consultan sin credenciales de usuario."""
    client.post("/corrales/", json=_CORRAL_VALIDO, headers=header_auth())
    respuesta = client.get("/corrales/")
    assert respuesta.status_code == 200
    assert len(respuesta.json()) == 1


def test_eliminar_corral_sin_token_devuelve_401():
    creado = client.post("/corrales/", json=_CORRAL_VALIDO, headers=header_auth())
    corral_id = creado.json()["id"]

    respuesta = client.delete(f"/corrales/{corral_id}")
    assert respuesta.status_code == 401

    # y confirmamos que efectivamente no se borró
    assert client.get("/corrales/").json() != []
