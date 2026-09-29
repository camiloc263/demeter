from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# Molde para la petición a la IA
class DatosNutricion(BaseModel):
    edad_dias: int = Field(..., ge=21, le=180, description="Edad del cerdo en días")
    peso_actual_kg: float = Field(..., gt=0, le=250, description="Peso actual en kg")
    temperatura_c: float = Field(..., ge=-10, le=55, description="Temperatura ambiental")

# Molde para guardar el evento de alimentación (Lógica RFID/Comedero)
class RegistroComidaCreate(BaseModel):
    id_cerdo_rfid: str = Field(..., description="Código RFID del collar o crotal del cerdo")
    corral: str = Field(..., description="Nombre del corral")
    racion_servida_kg: float = Field(..., gt=0)

class RegistroComidaResponse(RegistroComidaCreate):
    id: int
    fecha_hora: datetime

    class Config:
        from_attributes = True