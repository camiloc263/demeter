from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class RegistroBase(BaseModel):
    corral: str = Field(..., description="Nombre del corral que recibió el alimento")
    tipo_alimento: str = Field(..., description="Tipo de concentrado o dieta")
    cantidad_kg: float = Field(..., gt=0, description="Kilos de alimento servidos")

class RegistroCreate(RegistroBase):
    pass # Para crear, no pedimos fecha, la genera la base de datos

class RegistroResponse(RegistroBase):
    id: int
    fecha_hora: datetime

    class Config:
        from_attributes = True

# 4. ESQUEMA DE ACTUALIZACIÓN: Campos opcionales para corregir errores
class RegistroUpdate(BaseModel):
    corral: Optional[str] = Field(None, description="Corregir nombre del corral")
    tipo_alimento: Optional[str] = Field(None, description="Corregir tipo de dieta")
    cantidad_kg: Optional[float] = Field(None, gt=0, description="Corregir kilos servidos")