from fastapi import FastAPI
from db.database import engine
from db import models
from api import rutas_iot

# Crear las tablas en la base de datos
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Microservicio IoT - Granja Demeter",
    description="Motor de ingesta y análisis de datos de sensores ambientales",
    version="1.0.0"
)

# Conectamos nuestras rutas al motor principal
app.include_router(rutas_iot.router)