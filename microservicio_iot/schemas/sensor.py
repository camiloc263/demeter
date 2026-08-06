from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class LecturaBase(BaseModel):
    corral: str = Field(..., description="Nombre del corral monitoreado")
    temperatura_c: float = Field(..., description="Temperatura en grados centígrados")
    humedad_pct: float = Field(..., ge=0, le=100, description="Humedad relativa (0-100%)")

class LecturaCreate(LecturaBase):
    pass

class LecturaResponse(LecturaBase):
    id: int
    fecha_hora: datetime
    
    class Config:
        from_attributes = True