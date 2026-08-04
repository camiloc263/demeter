from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt

# Configuración de hashing para contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuración para el Token JWT (En producción esto va en variables de entorno)
SECRET_KEY = "tu_clave_secreta_super_segura_demeter_granja"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 # El token expira en 1 hora

def verificar_password(password_plana: str, password_hashed: str) -> bool:
    """Compara una contraseña en texto plano con el hash guardado en la base de datos."""
    return pwd_context.verify(password_plana, password_hashed)

def encriptar_password(password: str) -> str:
    """Genera un hash seguro e irreversible a partir de la contraseña del usuario."""
    return pwd_context.hash(password)

def crear_token_acceso(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Genera un Token JWT firmado digitalmente."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt