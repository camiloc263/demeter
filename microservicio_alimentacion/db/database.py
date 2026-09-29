import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Ruta absoluta anclada a este servicio (no depende del directorio de trabajo
# desde el que se lance el proceso, y no colisiona con otros servicios).
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.join(_BASE_DIR, 'alimentacion.db')}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()