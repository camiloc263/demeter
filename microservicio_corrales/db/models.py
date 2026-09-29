import os

from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ruta absoluta anclada a este servicio (no depende del directorio de trabajo
# desde el que se lance el proceso).
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
engine = create_engine(f"sqlite:///{os.path.join(_BASE_DIR, 'corrales.db')}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class CorralORM(Base):
    __tablename__ = "corrales"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True, nullable=False)
    capacidad_maxima = Column(Integer, nullable=False)

    ancho_m = Column(Float, nullable=False)
    largo_m = Column(Float, nullable=False)
    area_m2 = Column(Float, nullable=False) # Aquí guardaremos el resultado
    etapa = Column(String, nullable=False) # Nueva columna para la etapa