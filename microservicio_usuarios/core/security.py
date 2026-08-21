from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
import hashlib

# Configuración de hashing para contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuración para el Token JWT (En producción esto va en variables de entorno)
SECRET_KEY = "tu_clave_secreta_super_segura_demeter_granja"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60          # 1 hora
REFRESH_TOKEN_EXPIRE_DAYS = 7             # 7 días

# ----------------------------------------------------------------------
#   Funciones de contraseña
# ----------------------------------------------------------------------
def verificar_password(password_plana: str, password_hashed: str) -> bool:
    """Compara una contraseña en texto plano con el hash guardado en la base de datos."""
    return pwd_context.verify(password_plana, password_hashed)

def encriptar_password(password: str) -> str:
    """Genera un hash seguro e irreversible a partir de la contraseña del usuario."""
    return pwd_context.hash(password)

# ----------------------------------------------------------------------
#   JWT – Access token
# ----------------------------------------------------------------------
def crear_token_acceso(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Genera un Token JWT firmado digitalmente (access token)."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ----------------------------------------------------------------------
#   JWT – Refresh token
# ----------------------------------------------------------------------
def crear_token_refresco(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Genera un Token JWT con duración de refresco (refresh token)."""
    if expires_delta is None:
        expires_delta = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ----------------------------------------------------------------------
#   Hash de refresh token (para almacenamiento seguro)
# ----------------------------------------------------------------------
def hash_refresh_token(token: str) -> str:
    """Devuelve el hash SHA‑256 del refresh token."""
    return hashlib.sha256(token.encode()).hexdigest()

def verify_refresh_token(plain_token: str, stored_hash: str) -> bool:
    """Comprueba que el refresh token plano coincide con el hash almacenado."""
    return hash_refresh_token(plain_token) == stored_hash