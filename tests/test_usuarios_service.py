import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from microservicio_usuarios.main import app
from microservicio_usuarios.db.models import Base, get_db

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


def test_health():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "OK"
    assert response.json()["service"] == "Usuarios"


def test_registro_y_login_exitoso():
    respuesta = client.post(
        "/usuarios/",
        json={"username": "ana", "rol": "empleado", "password": "clave123"},
    )
    assert respuesta.status_code == 200
    assert "password" not in respuesta.json()  # nunca se devuelve la contraseña/hash

    login = client.post("/usuarios/login", json={"username": "ana", "password": "clave123"})
    assert login.status_code == 200
    cuerpo = login.json()
    assert cuerpo["rol"] == "empleado"
    assert cuerpo["refresh_token"]
    assert cuerpo["access_token"]


def test_login_con_password_incorrecta_devuelve_401():
    client.post("/usuarios/", json={"username": "ana", "rol": "empleado", "password": "clave123"})
    respuesta = client.post("/usuarios/login", json={"username": "ana", "password": "otra-clave"})
    assert respuesta.status_code == 401


def test_listar_usuarios_sin_token_devuelve_401():
    respuesta = client.get("/usuarios/")
    assert respuesta.status_code == 401


def test_listar_usuarios_con_token_de_empleado_devuelve_403():
    respuesta = client.get("/usuarios/", headers=header_auth(rol="empleado"))
    assert respuesta.status_code == 403


def test_listar_usuarios_con_token_de_administrador_devuelve_200():
    client.post("/usuarios/", json={"username": "ana", "rol": "empleado", "password": "clave123"})
    respuesta = client.get("/usuarios/", headers=header_auth(rol="administrador"))
    assert respuesta.status_code == 200
    assert len(respuesta.json()) == 1
