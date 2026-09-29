# D:\proyectos\Demeter\core_compartido\demeter_core\esquemas.py
from pydantic import BaseModel

class DatosClimaPayload(BaseModel):
    """
    Esquema de entrada para transferir los datos ambientales 
    que evalúa el modelo de Machine Learning.
    """
    temperatura_c: float
    humedad_pct: float
    peso_promedio_kg: float

class AlertaWhatsAppPayload(BaseModel):
    """
    Esquema de salida para enviar las alertas formateadas 
    al microservicio de notificaciones.
    """
    numero_telefono: str
    corral: str
    racion_kg: float
    motivo_ia: str