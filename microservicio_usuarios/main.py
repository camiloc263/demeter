from fastapi import FastAPI
from db.models import engine, Base
from api import rutas_usuarios

# Crea la base de datos usuarios.db
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Usuarios y Seguridad",
    description="Microservicio encargado de gestionar accesos, administradores y empleados."
)

app.include_router(rutas_usuarios.router)