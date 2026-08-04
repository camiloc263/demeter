from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import models
from db.models import get_db
from schemas import corral
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

router = APIRouter(prefix="/corrales", tags=["Gestión de Corrales"])

@router.post("/", response_model=corral.CorralResponse)
def crear_corral(nuevo_corral: corral.CorralCreate, db: Session = Depends(get_db)):
    """Crea un corral y calcula su área automáticamente."""
    
    # 1. Convertimos los datos que envió el usuario a un diccionario manipulable
    datos_corral = nuevo_corral.model_dump()
    
    # 2. CÁLCULO AUTOMÁTICO DEL ÁREA (Ancho x Largo)
    area_calculada = datos_corral["ancho_m"] * datos_corral["largo_m"]
    
    # 3. Inyectamos el resultado en el diccionario antes de enviarlo a la Base de Datos
    datos_corral["area_m2"] = area_calculada
    
    # 4. Guardamos en la base de datos
    db_corral = models.CorralORM(**datos_corral)
    db.add(db_corral)
    db.commit()
    db.refresh(db_corral)
    
    return db_corral

@router.get("/{nombre_corral}", response_model=corral.CorralResponse)
def obtener_corral_por_nombre(nombre_corral: str, db: Session = Depends(get_db)):
    db_corral = db.query(models.CorralORM).filter(models.CorralORM.nombre == nombre_corral).first()
    if not db_corral:
        raise HTTPException(status_code=404, detail="El corral no existe.")
    return db_corral
@router.get("/", response_model=List[corral.CorralResponse])
def obtener_todos_los_corrales(db: Session = Depends(get_db)):
    """Obtiene la lista de todos los corrales construidos en la granja."""
    return db.query(models.CorralORM).all()


@router.patch("/{corral_id}", response_model=corral.CorralResponse)
def actualizar_corral(corral_id: int, datos_actualizados: corral.CorralUpdate, db: Session = Depends(get_db)):
    """Actualiza los datos de un corral y recalcula el área si es necesario."""
    db_corral = db.query(models.CorralORM).filter(models.CorralORM.id == corral_id).first()
    
    if not db_corral:
        raise HTTPException(status_code=404, detail="Corral no encontrado.")

    # exclude_unset=True toma solo los datos que el usuario envió en Postman
    datos_dict = datos_actualizados.model_dump(exclude_unset=True)

    # REGLA DE NEGOCIO: Si modifican las medidas, recalculamos el área
    if "ancho_m" in datos_dict or "largo_m" in datos_dict:
        # Tomamos el dato nuevo, o el viejo si no lo enviaron
        nuevo_ancho = datos_dict.get("ancho_m", db_corral.ancho_m)
        nuevo_largo = datos_dict.get("largo_m", db_corral.largo_m)
        datos_dict["area_m2"] = nuevo_ancho * nuevo_largo # Recálculo automático

    # Aplicamos los cambios
    for clave, valor in datos_dict.items():
        setattr(db_corral, clave, valor)

    db.commit()
    db.refresh(db_corral)
    return db_corral


@router.delete("/{corral_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_corral(corral_id: int, db: Session = Depends(get_db)):
    """Demuele (elimina) un corral del sistema."""
    db_corral = db.query(models.CorralORM).filter(models.CorralORM.id == corral_id).first()
    
    if not db_corral:
        raise HTTPException(status_code=404, detail="Corral no encontrado.")

    db.delete(db_corral)
    db.commit()
    return None