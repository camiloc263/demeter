# Registro de alimentación agregado por corral (un lote de comida para todo
# el corral). Complementario a microservicio_alimentacion_ia, que registra
# eventos individuales de comedero RFID por cerdo y ofrece predicción de
# dieta con IA — no son duplicados, son dos niveles de granularidad del
# mismo dominio.
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from starlette.requests import Request

# Rate limiting configuration
limiter = Limiter(key_func=get_remote_address, default_limits=["120/minute"])

app = FastAPI(
    title="Microservicio de Alimentación por Corral - Granja Demeter",
    description="Registra raciones agregadas de alimento entregadas a cada corral (lote, no por animal).",
    version="1.0.0",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

from .api.rutas_alimentacion import router

from .db.database import engine
from .db import models

models.Base.metadata.create_all(bind=engine)

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
@limiter.limit("10/minute")
async def health_check(request: Request):
    return {"status": "OK", "service": "Alimentación"}

if __name__ == "__main__":
    # Ejecutar desde la raíz del repositorio: python -m microservicio_alimentacion.main
    uvicorn.run("microservicio_alimentacion.main:app", host="0.0.0.0", port=8000, reload=True)