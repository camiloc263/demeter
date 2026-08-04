from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from .database import Base

class RegistroAlimentacionORM(Base):
    __tablename__ = "registros_alimentacion"

    id = Column(Integer, primary_key=True, index=True)
    corral = Column(String, index=True, nullable=False)
    tipo_alimento = Column(String, nullable=False) # Ej: Engorde, Gestación
    cantidad_kg = Column(Float, nullable=False)
    fecha_hora = Column(DateTime, default=datetime.utcnow) # Se guarda la hora automáticamente