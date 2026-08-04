from pydantic import BaseModel, Field
from enum import Enum

# 1. Definimos los roles permitidos de forma estricta
class RolUsuario(str, Enum):
    administrador = "administrador"
    empleado = "empleado"

# 2. Esquema Base
class UsuarioBase(BaseModel):
    username: str = Field(..., description="Nombre de usuario para iniciar sesión")
    rol: RolUsuario = Field(..., description="Rol del usuario en el sistema")
    activo: bool = Field(default=True, description="Indica si el usuario tiene acceso al sistema")

# 3. Esquema para Crear (Requiere contraseña)
class UsuarioCreate(UsuarioBase):
    password: str = Field(..., min_length=6, description="Contraseña del usuario (mínimo 6 caracteres)")

# 4. Esquema de Respuesta (NUNCA devolvemos la contraseña por seguridad)
class UsuarioResponse(UsuarioBase):
    id: int
    
    class Config:
        from_attributes = True

      
# 5. Esquema para recibir los datos de inicio de sesión
class LoginRequest(BaseModel):
    username: str
    password: str

# 6. Esquema de respuesta cuando el Login es exitoso
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    rol: str