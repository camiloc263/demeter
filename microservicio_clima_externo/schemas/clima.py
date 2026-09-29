from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class CoordenadasGranja(BaseModel):
    nombre_granja: str = Field(..., description="Nombre comercial de la granja")
    latitud: float = Field(..., description="Latitud GPS")
    longitud: float = Field(..., description="Longitud GPS")
    peso_promedio_kg: Optional[float] = Field(100.0, description="Peso promedio de los cerdos en kg para la IA")

class RegistroClimaResponse(BaseModel):
    id: int
    nombre_granja: str
    latitud: float
    longitud: float
    temperatura_c: float
    humedad_pct: float
    estado_riesgo: Optional[str]
    mensaje_ia: Optional[str]
    certeza_ia: Optional[float]
    fecha_registro: datetime

    class Config:
        from_attributes = True