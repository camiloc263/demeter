from pydantic import BaseModel, Field
from typing import Optional
from demeter_core.enums import EtapaCorral

# 1. ESQUEMA BASE: Lo que recibimos del usuario
class CorralBase(BaseModel):
    nombre: str = Field(..., description="Nombre único del corral (Ej: Corral A)")
    capacidad_maxima: int = Field(..., gt=0, description="Número máximo de cerdos")
    
    # Nuevos campos físicos
    ancho_m: float = Field(..., gt=0, description="Ancho del corral en metros")
    largo_m: float = Field(..., gt=0, description="Largo del corral en metros")
    etapa: EtapaCorral = Field(..., description="Etapa productiva para la que fue diseñado el corral")

class CorralCreate(CorralBase):
    pass

# 2. ESQUEMA DE RESPUESTA: Lo que devolvemos (incluye ID y el Área calculada)
class CorralResponse(CorralBase):
    id: int
    area_m2: float = Field(..., description="Área total en metros cuadrados (Generada automáticamente)")
    
    class Config:
        from_attributes = True

        # 3. ESQUEMA DE ACTUALIZACIÓN: Campos opcionales
class CorralUpdate(BaseModel):
    nombre: Optional[str] = Field(None, description="Nuevo nombre del corral")
    capacidad_maxima: Optional[int] = Field(None, gt=0, description="Nueva capacidad")
    ancho_m: Optional[float] = Field(None, gt=0, description="Nuevo ancho")
    largo_m: Optional[float] = Field(None, gt=0, description="Nuevo largo")
    etapa: Optional[EtapaCorral] = Field(None, description="Nueva etapa productiva")