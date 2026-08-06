from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base
import datetime

Base = declarative_base()

class LecturaSensorORM(Base):
    __tablename__ = "lecturas_iot"
    
    id = Column(Integer, primary_key=True, index=True)
    corral = Column(String, index=True, nullable=False)
    temperatura_c = Column(Float, nullable=False)
    humedad_pct = Column(Float, nullable=False)
    # Guardamos el momento exacto en que el sensor envió el dato
    fecha_hora = Column(DateTime, default=datetime.datetime.utcnow, index=True)