from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

# 1. ESQUEMA BASE: Lo que comparten todos los cerdos
class CerdoBase(BaseModel):
    etiqueta: str = Field(..., description="Identificador único del cerdo (Ej: C-001)")
    raza: Optional[str] = Field(None, description="Raza del animal (Ej: Duroc)")
    fecha_nacimiento: date = Field(..., description="Fecha en formato YYYY-MM-DD")

    # Validamos por seguridad que el peso siempre sea mayor a 0 (gt=0)
    peso_kg: float = Field(..., gt=0, description="Peso en kilogramos")
    corral: str = Field(..., description="Ubicación actual en la granja")

# 2. ESQUEMA DE CREACIÓN: Lo que pedimos cuando registramos un cerdo nuevo
class CerdoCreate(CerdoBase):
    pass # Es idéntico al Base. No pedimos ID porque la base de datos lo genera solo.

# 3. ESQUEMA DE RESPUESTA: Lo que el sistema devuelve cuando consultamos
class CerdoResponse(CerdoBase):
    id: int # Aquí sí incluimos el ID interno de la base de datos
    
    class Config:
        # Esto le dice a Pydantic que sea compatible con bases de datos (ORM)
        from_attributes = True


  # 4. ESQUEMA DE ACTUALIZACIÓN: Campos opcionales para no sobrescribir todo
class CerdoUpdate(BaseModel):
    etiqueta: Optional[str] = Field(None, description="Identificador único")
    raza: Optional[str] = Field(None, description="Raza del animal")
    fecha_nacimiento: Optional[date] = None
    peso_kg: Optional[float] = Field(None, gt=0, description="Nuevo peso en kg")
    corral: Optional[str] = Field(None, description="Nueva ubicación")      