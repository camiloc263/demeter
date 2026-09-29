import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ruta absoluta anclada a este servicio: evita colisionar con el archivo
# alimentacion.db de microservicio_alimentacion cuando ambos corren desde
# el mismo directorio de trabajo (la raíz del repo).
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.join(_BASE_DIR, 'alimentacion_ia.db')}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()