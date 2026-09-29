from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base
import datetime

Base = declarative_base()

class HistorialClimaExternoORM(Base):
    __tablename__ = "historial_clima_externo"

    id = Column(Integer, primary_key=True, index=True)
    nombre_granja = Column(String, index=True, nullable=False)
    latitud = Column(Float, nullable=False)
    longitud = Column(Float, nullable=False)
    temperatura_c = Column(Float, nullable=False)
    humedad_pct = Column(Float, nullable=False)
    
    # Diagnóstico que nos entregará el microservicio de IA (puerto 8006)
    estado_riesgo = Column(String, nullable=True)
    mensaje_ia = Column(String, nullable=True)
    certeza_ia = Column(Float, nullable=True)
    
    fecha_registro = Column(DateTime, default=datetime.datetime.utcnow, index=True)