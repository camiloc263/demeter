from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Crearemos una base de datos exclusiva para IoT
SQLALCHEMY_DATABASE_URL = "sqlite:///./iot.db"

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