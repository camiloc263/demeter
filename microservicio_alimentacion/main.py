from fastapi import FastAPI
from db.database import engine, Base
from db import models
from api import rutas_alimentacion

# Crea las tablas en alimentacion.db
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Alimentación - Granja Porcina",
    description="Microservicio para registrar el consumo de comida.",
    version="1.0.0"
)

app.include_router(rutas_alimentacion.router)

@app.get("/", tags=["Sistema"])
def estado_del_sistema():
    return {"mensaje": "Microservicio de Alimentación en línea", "estado": "OK"}