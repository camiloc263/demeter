from sqlalchemy import Column, Integer, String, Float, Date
from .database import Base # Importamos la base que acabamos de crear

class CerdoORM(Base):
    __tablename__ = "cerdos" # Nombre de la tabla en la base de datos

    # Definimos las columnas
    id = Column(Integer, primary_key=True, index=True)
    etiqueta = Column(String, unique=True, index=True, nullable=False)
    raza = Column(String, nullable=True) # Puede estar vacío
    fecha_nacimiento = Column(Date, nullable=False)
    peso_kg = Column(Float, nullable=False)
    corral = Column(String, nullable=False)