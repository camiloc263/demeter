# Registro de alimentación por comedero RFID (evento individual por cerdo) +
# predicción de dieta con IA. Complementario a microservicio_alimentacion,
# que registra raciones agregadas por corral: ver el docstring de
# api/rutas_alimentacion.py para la diferencia de responsabilidad entre ambos.
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from .api.rutas_alimentacion import router

from .db.database import engine
from .db import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Microservicio de Alimentación por RFID + IA Nutricional - Granja Demeter",
    description="Registra eventos de comedero por cerdo individual (RFID) y recomienda raciones con Machine Learning.",
    version="1.0.0",
)
app.state.limiter = Limiter(key_func=get_remote_address, default_limits=["120/minute"])
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.include_router(router)

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

@app.get("/", tags=["Health"])
async def health_check():
    return {"status": "OK", "service": "Alimentación IA"}

if __name__ == "__main__":
    # Ejecutar desde la raíz del repositorio: python -m microservicio_alimentacion_ia.main
    uvicorn.run("microservicio_alimentacion_ia.main:app", host="0.0.0.0", port=8002, reload=True)