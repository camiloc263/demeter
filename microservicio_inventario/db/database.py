import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

# Ruta absoluta anclada a este servicio (no depende del directorio de trabajo
# desde el que se lance el proceso).
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.join(_BASE_DIR, 'cerdo.db')}"

# 2. MOTOR DE CONEXIÓN
# check_same_thread=False es necesario solo para SQLite en FastAPI
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. SESIÓN (La "ventana" temporal por donde enviamos datos)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. BASE (La clase madre para nuestras tablas)
Base = declarative_base()

# 5. FUNCIÓN DE AYUDA (Para usar en nuestras rutas más adelante)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() # Siempre cerramos la conexión por seguridad