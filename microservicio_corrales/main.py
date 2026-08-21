import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from api.rutas_corrales import router

from db.database import engine
from db import models

# Crear tablas si no existen
models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(
    SlowAPIMiddleware,
    limiter=Limiter(key_func=get_remote_address, default_limits=["120/minute"])
)

# CORS permisivo (ajustar en producción)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/", tags=["Health"])
async def health_check():
    return {"status": "OK", "service": "Corrales"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)