from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

# 1. URL DE LA BASE DE DATOS
# Creará un archivo llamado 'granja.db' en tu carpeta raíz
SQLALCHEMY_DATABASE_URL = "sqlite:///./cerdo.db"

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