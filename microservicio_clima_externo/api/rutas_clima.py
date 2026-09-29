from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..db.database import get_db
from ..db import models
from ..schemas import clima
from ..services import meteo_client, ia_client

router = APIRouter(prefix="/clima_externo", tags=["Sensores Virtuales & Diagnóstico IA"])

@router.post("/consultar_y_guardar", response_model=clima.RegistroClimaResponse)
def consultar_guardar_y_analizar(datos: clima.CoordenadasGranja, db: Session = Depends(get_db)):
    """
    1. Obtiene el clima por GPS desde Open-Meteo.
    2. Consulta al microservicio_ia (8006) para evaluación de estrés calórico.
    3. Guarda la lectura completa en la base de datos local.
    """
    # 1. Consultar satélite
    try:
        clima_satelital = meteo_client.obtener_clima_actual(datos.latitud, datos.longitud)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Error consultando satélite: {str(e)}")
        
    temp = clima_satelital["temperatura_c"]
    hum = clima_satelital["humedad_pct"]
    
    # 2. Consultar el cerebro de la IA (puerto 8006)
    prediccion_ia = ia_client.consultar_ia_bienestar(
        temperatura_c=temp,
        humedad_pct=hum,
        peso_promedio_kg=datos.peso_promedio_kg
    )
    
    traductor_riesgo = {
        0: "ÓPTIMO 🟢",
        1: "ALERTA 🟡",
        2: "PELIGRO 🔴"
    }
    
    codigo_estado = prediccion_ia.get("estado_codigo", -1)
    estado_texto = traductor_riesgo.get(codigo_estado, "DESCONOCIDO ⚪")
    
    # 3. Guardar en la Base de Datos
    nuevo_registro = models.HistorialClimaExternoORM(
        nombre_granja=datos.nombre_granja,
        latitud=datos.latitud,
        longitud=datos.longitud,
        temperatura_c=temp,
        humedad_pct=hum,
        estado_riesgo=estado_texto,
        mensaje_ia=prediccion_ia.get("mensaje", "Sin respuesta"),
        certeza_ia=prediccion_ia.get("certeza_porcentaje", 0.0)
    )
    
    db.add(nuevo_registro)
    db.commit()
    db.refresh(nuevo_registro)
    
    return nuevo_registro

@router.get("/historial/{nombre_granja}", response_model=List[clima.RegistroClimaResponse])
def obtener_historial_granja(nombre_granja: str, db: Session = Depends(get_db)):
    """Consulta todas las lecturas históricas guardadas para una granja."""
    registros = db.query(models.HistorialClimaExternoORM)\
                  .filter(models.HistorialClimaExternoORM.nombre_granja == nombre_granja)\
                  .order_by(models.HistorialClimaExternoORM.fecha_registro.desc())\
                  .all()
    return registros