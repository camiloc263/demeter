from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Literal, Optional

class SolicitudOrden(BaseModel):
    nombre_corral: str = Field(..., description="Nombre del corral a alimentar")
    numero_cerdos: int = Field(..., gt=0, description="Cantidad de cerdos en el lote")
    peso_promedio_kg: float = Field(..., gt=0, description="Peso promedio estimado del lote")
    etapa: Literal["LEVANTE", "ENGORDE", "GESTACION", "LACTANCIA", "FINALIZACION"]
    temperatura_actual_c: float = Field(..., description="Temperatura ambiental actual")

class RecetaLote(BaseModel):
    maiz_amarillo_kg: float
    mogolla_fina_kg: float
    mogolla_gruesa_kg: float
    cal_agricola_kg: float
    sal_mineral_kg: float
    harina_pescado_kg: float
    liquido_hidratacion_litros: float

class OrdenRespuesta(BaseModel):
    id: int
    codigo_orden: str
    corral_objetivo: str
    total_raciones_kg: float
    receta_preparacion_lote: RecetaLote
    instrucciones_sop: List[str]
    estado: str
    fecha_creacion: datetime

    class Config:
        from_attributes = True

class ConfirmacionOrden(BaseModel):
    operario_responsable: str
    observaciones: Optional[str] = None