from fastapi import FastAPI
from db.models import engine, Base
from api import rutas_corrales

Base.metadata.create_all(bind=engine)

app = FastAPI(title="API de Corrales")
app.include_router(rutas_corrales.router)