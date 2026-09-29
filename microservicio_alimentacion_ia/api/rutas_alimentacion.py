"""
Rutas de alimentación por comedero RFID + predicción de dieta con IA.

Distinto de `microservicio_alimentacion`: ese servicio registra raciones
agregadas por corral (un lote de comida para todo el corral); este servicio
registra cada evento individual de un comedero automático identificado por
el RFID/crotal del cerdo, y además ofrece una recomendación de ración vía
un modelo de Machine Learning (`/predecir_dieta`). Ambos servicios son
complementarios, no duplicados: uno es el resumen por corral, el otro es el
detalle por animal.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import joblib
import os
import logging

from ..db.database import get_db
from ..db import repository
from ..schemas import nutricion
from ..services import inventario_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/alimentacion", tags=["Comederos e IA Nutricional"])

# Load model with explicit error capture
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "modelo_nutricion.pkl")
try:
    modelo_nutricion = joblib.load(MODEL_PATH)
    logger.info("Modelo de nutrición cargado correctamente.")
except Exception as exc:
    modelo_nutricion = None
    logger.error(f"Error al cargar el modelo de nutrición desde '{MODEL_PATH}': {exc}")

@router.post("/predecir_dieta")
def predecir_dieta(datos: nutricion.DatosNutricion):
    """Calcula la ración recomendada por la IA según edad, peso y temperatura."""
    if not modelo_nutricion:
        # Include the original exception in the detail for diagnostics
        raise HTTPException(
            status_code=500,
            detail="El modelo de nutrición no está disponible. Consulte los logs para más información."
        )
    try:
        entrada = [[datos.edad_dias, datos.peso_actual_kg, datos.temperatura_c]]
        racion_predicha = round(modelo_nutricion.predict(entrada)[0], 2)
    except Exception as e:
        logger.exception("Error durante la predicción.")
        raise HTTPException(
            status_code=500,
            detail=f"Error inesperado al realizar la predicción: {str(e)}"
        )
    advertencia = ""
    if datos.temperatura_c > 28:
        advertencia = "⚠️ Alta temperatura. Ración reducida preventivamente por pérdida de apetito."
    return {
        "racion_recomendada_kg": racion_predicha,
        "costo_estimado_usd": round(racion_predicha * 0.40, 2),
        "analisis": advertencia if advertencia else "Condiciones óptimas para alimentación."
    }

@router.post("/registrar_comida", response_model=nutricion.RegistroComidaResponse)
def registrar_comida(comida: nutricion.RegistroComidaCreate, db: Session = Depends(get_db)):
    """Registra la ración servida a un cerdo específico mediante su RFID,
    validando primero contra el Inventario que ese RFID pertenece a un cerdo
    realmente asignado a ese corral."""
    inventario_client.verificar_cerdo_en_corral(comida.corral, comida.id_cerdo_rfid)
    return repository.registrar_comida(db, comida)

@router.get("/historial/{id_cerdo_rfid}", response_model=List[nutricion.RegistroComidaResponse])
def obtener_historial_cerdo(id_cerdo_rfid: str, db: Session = Depends(get_db)):
    """Consulta todas las veces que ha comido un cerdo determinado."""
    return repository.obtener_historial_cerdo(db, id_cerdo_rfid)
