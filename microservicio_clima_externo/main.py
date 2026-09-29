import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db.database import engine
from .db import models
from .api import rutas_clima

# Crear las tablas automáticamente en la base de datos (SQLite)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sensores Virtuales + IA - Granja Demeter",
    description="Obtiene clima satelital, consulta al microservicio_ia (8006) y guarda historial",
    version="2.0.0"
)

# CORS: la autenticación va por header Authorization (Bearer), no por cookies,
# así que no se necesita allow_credentials=True — combinarlo con origin "*"
# es además inválido según el spec de CORS.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conectar las rutas externas al archivo principal
app.include_router(rutas_clima.router)

@app.get("/", tags=["Health"])
async def health_check():
    return {"status": "OK", "service": "Clima Externo"}

if __name__ == "__main__":
    # Ejecutar desde la raíz del repositorio: python -m microservicio_clima_externo.main
    uvicorn.run("microservicio_clima_externo.main:app", host="0.0.0.0", port=8008, reload=True)