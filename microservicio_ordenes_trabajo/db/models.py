from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.orm import declarative_base
import datetime

Base = declarative_base()

class OrdenTrabajoORM(Base):
    __tablename__ = "ordenes_trabajo"

    id = Column(Integer, primary_key=True, index=True)
    codigo_orden = Column(String, unique=True, index=True, nullable=False)
    corral_objetivo = Column(String, index=True, nullable=False)
    total_raciones_kg = Column(Float, nullable=False)
    
    # Detalle de la mezcla guardado en JSON/Texto
    receta_json = Column(Text, nullable=False)
    instrucciones_json = Column(Text, nullable=False)
    
    estado = Column(String, default="PENDIENTE", index=True) # PENDIENTE / COMPLETADA
    operario_responsable = Column(String, nullable=True)
    observaciones = Column(String, nullable=True)
    
    fecha_creacion = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    fecha_completado = Column(DateTime, nullable=True)