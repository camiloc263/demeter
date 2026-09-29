from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..db.database import get_db
from ..db import models
from ..schemas import sensor
from ..services import corrales_client

router = APIRouter(prefix="/iot", tags=["Sensores Ambientales"])

@router.post("/", response_model=sensor.LecturaResponse)
def registrar_lectura(lectura: sensor.LecturaCreate, db: Session = Depends(get_db)):
    """Recibe y guarda un 'ping' de temperatura/humedad validando previamente la existencia del corral."""
    
    # 2. VALIDACIÓN CRUZADA: ¿Existe el corral en el microservicio de Corrales?
    corrales_client.verificar_corral_existe(lectura.corral)
    
    # 3. Si existe, guardamos la lectura en la base de datos IoT
    nueva_lectura = models.LecturaSensorORM(**lectura.model_dump())
    
    db.add(nueva_lectura)
    db.commit()
    db.refresh(nueva_lectura)
    return nueva_lectura

@router.get("/corral/{nombre_corral}", response_model=List[sensor.LecturaResponse])
def obtener_lecturas_corral(nombre_corral: str, limite: int = 10, db: Session = Depends(get_db)):
    """Obtiene las últimas 'N' lecturas ambientales de un corral específico."""
    lecturas = db.query(models.LecturaSensorORM)\
                 .filter(models.LecturaSensorORM.corral == nombre_corral)\
                 .order_by(models.LecturaSensorORM.fecha_hora.desc())\
                 .limit(limite)\
                 .all()
                 
    if not lecturas:
        raise HTTPException(status_code=404, detail=f"No hay lecturas registradas para el {nombre_corral}")
        
    return lecturas