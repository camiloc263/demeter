import os
import sys
from datetime import datetime, timedelta

from jose import jwt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "core_compartido")))

from demeter_core.auth import JWT_ALGORITHM, JWT_SECRET_KEY  # noqa: E402


def crear_token_prueba(username: str = "usuario_de_prueba", rol: str = "empleado", minutos: int = 30) -> str:
    """Genera un JWT válido firmado con la misma clave que usan los servicios, para usar en tests."""
    payload = {"sub": username, "rol": rol, "exp": datetime.utcnow() + timedelta(minutes=minutos)}
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def header_auth(username: str = "usuario_de_prueba", rol: str = "empleado") -> dict:
    """Header Authorization listo para pasar a TestClient: headers=header_auth(rol="administrador")."""
    return {"Authorization": f"Bearer {crear_token_prueba(username=username, rol=rol)}"}
