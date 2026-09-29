import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from .api.rutas_usuarios import router

from .db.models import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.state.limiter = Limiter(key_func=get_remote_address, default_limits=["120/minute"])
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

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

app.include_router(router)

@app.get("/", tags=["Health"])
async def health_check():
    return {"status": "OK", "service": "Usuarios"}

if __name__ == "__main__":
    # Ejecutar desde la raíz del repositorio: python -m microservicio_usuarios.main
    uvicorn.run("microservicio_usuarios.main:app", host="0.0.0.0", port=8005, reload=True)