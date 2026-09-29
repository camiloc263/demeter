import os
import sys
from datetime import datetime, timedelta

import pytest
from fastapi import HTTPException
from jose import jwt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "core_compartido")))

from demeter_core.auth import (  # noqa: E402
    JWT_ALGORITHM,
    JWT_SECRET_KEY,
    UsuarioToken,
    requiere_rol,
    verificar_token,
)


def _token(sub="ana", rol="empleado", minutos=30, secret=None):
    payload = {"sub": sub, "rol": rol, "exp": datetime.utcnow() + timedelta(minutes=minutos)}
    return jwt.encode(payload, secret or JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def test_verificar_token_valido_devuelve_usuario():
    usuario = verificar_token(_token(sub="ana", rol="administrador"))
    assert usuario == UsuarioToken(username="ana", rol="administrador")


def test_verificar_token_expirado_levanta_401():
    with pytest.raises(HTTPException) as exc:
        verificar_token(_token(minutos=-1))
    assert exc.value.status_code == 401


def test_verificar_token_firmado_con_otra_clave_levanta_401():
    with pytest.raises(HTTPException) as exc:
        verificar_token(_token(secret="clave-equivocada-de-un-atacante"))
    assert exc.value.status_code == 401


def test_verificar_token_malformado_levanta_401():
    with pytest.raises(HTTPException) as exc:
        verificar_token("esto-no-es-un-jwt")
    assert exc.value.status_code == 401


def test_verificar_token_sin_sub_ni_rol_levanta_401():
    payload = {"exp": datetime.utcnow() + timedelta(minutes=5)}
    token_incompleto = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    with pytest.raises(HTTPException) as exc:
        verificar_token(token_incompleto)
    assert exc.value.status_code == 401


def test_requiere_rol_permite_el_rol_correcto():
    verificar_admin = requiere_rol("administrador")
    resultado = verificar_admin(usuario=UsuarioToken(username="ana", rol="administrador"))
    assert resultado.username == "ana"


def test_requiere_rol_rechaza_rol_incorrecto_con_403():
    verificar_admin = requiere_rol("administrador")
    with pytest.raises(HTTPException) as exc:
        verificar_admin(usuario=UsuarioToken(username="juan", rol="empleado"))
    assert exc.value.status_code == 403


def test_requiere_rol_acepta_lista_de_roles():
    verificar_cualquiera = requiere_rol("administrador", "empleado")
    resultado = verificar_cualquiera(usuario=UsuarioToken(username="juan", rol="empleado"))
    assert resultado.rol == "empleado"
