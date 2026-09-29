from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base
import datetime

Base = declarative_base()

class RegistroComidaORM(Base):
    __tablename__ = "registros_alimentacion"

    id = Column(Integer, primary_key=True, index=True)
    id_cerdo_rfid = Column(String, index=True, nullable=False)
    corral = Column(String, index=True, nullable=False)
    racion_servida_kg = Column(Float, nullable=False)
    fecha_hora = Column(DateTime, default=datetime.datetime.utcnow, index=True)