from fastapi import FastAPI
from db.database import engine, Base 
from db import models
from api import rutas_cerdos

# --------------------------------------------------------
# INICIALIZACIÓN DE LA APLICACIÓN (Capa de Presentación)
# --------------------------------------------------------
# Creamos la instancia de FastAPI con el título de tu proyecto
app = FastAPI(
    title="API de Inventario - Granja Porcina",
    description="Microservicio para la gestión de animales, razas y corrales.",
    version="1.0.0"
)

# Creamos las tablas en la base de datos (si no existen)
Base.metadata.create_all(bind=engine)

# --------------------------------------------------------
# RUTAS BÁSICAS (Endpoints)
# --------------------------------------------------------
@app.get("/", tags=["Sistema"])
def estado_del_sistema():
    """
    Ruta de prueba para verificar que el microservicio está funcionando.
    (Health Check)
    """
    return {
        "mensaje": "¡Hola, Arquitecto! El Microservicio de Inventario está en línea y funcionando.",
        "estado": "OK"
    }

# Conectamos las rutas del módulo de cerdos a la aplicación principal
app.include_router(rutas_cerdos.router) 
