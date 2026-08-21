import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware import Middleware
from slowapi import Limiter
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware import Middleware
from starlette.requests import Request
from slowapi.util import get_remote_address

# Rate limiting configuration
limiter = Limiter(key_func=get_remote_address, default_limits=["120/minute"])

# FastAPI app with SlowAPI middleware
app = FastAPI(
    middleware=[
        Middleware(SlowAPIMiddleware, limiter=limiter)
    ]
)

from api.rutas_alimentacion import router

from db.database import engine
from db import models

models.Base.metadata.create_all(bind=engine)

app.include_router(router)

# CORS (adjust origins for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Health"])
@limiter.limit("10/minute")
async def health_check():
    return {"status": "OK", "service": "Alimentación"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)