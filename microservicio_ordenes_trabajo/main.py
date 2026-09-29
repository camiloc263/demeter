import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db.database import engine
from .db import models
from .api import rutas_ordenes

# Crear las tablas automáticamente
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Microservicio de Órdenes de Trabajo - Granja Demeter",
    description="Generación y control de preparación manual de alimento por lotes (SOP)",
    version="1.0.0"
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

app.include_router(rutas_ordenes.router)

@app.get("/", tags=["Health"])
async def health_check():
    return {"status": "OK", "service": "Órdenes de Trabajo"}

if __name__ == "__main__":
    # Ejecutar desde la raíz del repositorio: python -m microservicio_ordenes_trabajo.main
    uvicorn.run("microservicio_ordenes_trabajo.main:app", host="0.0.0.0", port=8009, reload=True)