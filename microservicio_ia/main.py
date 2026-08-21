import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from api.rutas_alimentacion import router

from db.database import engine
from db import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=os.getenv("APP_TITLE", "IA Avanzada Demeter - Random Forest"),
    description=os.getenv("APP_DESCRIPTION", "Motor de Machine Learning con análisis predictivo multidimensional"),
    version=os.getenv("APP_VERSION", "2.0.0")
)

# Rate limiting configuration
limiter = Limiter(key_func=get_remote_address, default_limits=["120/minute"])
app.add_middleware(SlowAPIMiddleware, limiter=limiter)

# CORS permissivo (ajustar en producción)
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
    return {"status": "OK", "service": "Alimentación IA"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)