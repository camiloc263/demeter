# D:\proyectos\Demeter\core_compartido\demeter_core\auth.py
"""Verificación de JWT compartida entre microservicios.

`microservicio_usuarios` es el único que emite tokens (ver su propio
`core/security.py`, que reutiliza `JWT_SECRET_KEY`/`JWT_ALGORITHM` de este
módulo para firmarlos); cualquier otro servicio que necesite proteger una
ruta solo necesita verificarlos, así que esa lógica vive aquí una sola vez
en vez de reimplementarse en cada servicio.

Todos los servicios deben compartir el mismo `JWT_SECRET_KEY` (variable de
entorno) para que un token emitido por usuarios sea válido en los demás. Si
ninguno la define, todos caen al mismo valor de desarrollo por defecto (ver
`_JWT_SECRET_KEY_DEV_DEFAULT` abajo), así que el sistema sigue funcionando
de forma consistente en local sin configuración adicional — pero antes de
desplegar a un entorno real hay que fijar `JWT_SECRET_KEY` explícitamente
(y de forma idéntica) en cada servicio.
"""

from __future__ import annotations

import os
import warnings

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel

_JWT_SECRET_KEY_DEV_DEFAULT = "dev-only-insecure-secret-cambiar-en-produccion"

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", _JWT_SECRET_KEY_DEV_DEFAULT)
JWT_ALGORITHM = "HS256"

if JWT_SECRET_KEY == _JWT_SECRET_KEY_DEV_DEFAULT:
    warnings.warn(
        "JWT_SECRET_KEY no está definido por variable de entorno; usando la clave de "
        "desarrollo por defecto (insegura). Defínela de forma idéntica en todos los "
        "servicios antes de desplegar a producción.",
        RuntimeWarning,
        stacklevel=2,
    )

# Solo se usa para que /docs muestre el botón "Authorize"; la validación real
# ocurre en verificar_token() sin importar por cuál ruta se haya pedido el token.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="usuarios/login", auto_error=True)


class UsuarioToken(BaseModel):
    """Identidad del usuario autenticado, extraída del payload del JWT."""

    username: str
    rol: str


def verificar_token(token: str) -> UsuarioToken:
    """Decodifica y valida un JWT. Levanta 401 si es inválido, está mal firmado o expiró."""
    credenciales_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas o token expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except JWTError:
        raise credenciales_invalidas

    username = payload.get("sub")
    rol = payload.get("rol")
    if username is None or rol is None:
        raise credenciales_invalidas

    return UsuarioToken(username=username, rol=rol)


async def obtener_usuario_actual(token: str = Depends(oauth2_scheme)) -> UsuarioToken:
    """Dependencia de FastAPI: exige un Bearer token válido para acceder a la ruta."""
    return verificar_token(token)


def requiere_rol(*roles_permitidos: str):
    """Fábrica de dependencia: además de exigir un token válido, exige que el
    usuario tenga uno de los roles indicados (ej. `requiere_rol("administrador")`)."""

    def _verificar(usuario: UsuarioToken = Depends(obtener_usuario_actual)) -> UsuarioToken:
        if usuario.rol not in roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Esta acción requiere uno de estos roles: {', '.join(roles_permitidos)}.",
            )
        return usuario

    return _verificar
