import os

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ruta absoluta anclada a este servicio (no depende del directorio de trabajo
# desde el que se lance el proceso).
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
engine = create_engine(f"sqlite:///{os.path.join(_BASE_DIR, 'usuarios.db')}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UsuarioORM(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False) # Guardaremos la contraseña de forma segura
    rol = Column(String, nullable=False)
    activo = Column(Boolean, default=True)
    refresh_token_hash = Column(String, nullable=True)  # Hash del refresh token