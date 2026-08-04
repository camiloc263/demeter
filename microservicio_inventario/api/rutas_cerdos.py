from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.database import get_db
from schemas import cerdo
from db import repository
from services import corrales_client


# Creamos un "Router" para agrupar todas las rutas de los cerdos
router = APIRouter(prefix="/cerdos", tags=["Inventario de Cerdos"])

@router.post("/", response_model=cerdo.CerdoResponse)
def crear_cerdo(nuevo_cerdo: cerdo.CerdoCreate, db: Session = Depends(get_db)):
    """Registra un nuevo cerdo en la granja."""
    return repository.registrar_cerdo(db=db, cerdo_in=nuevo_cerdo)

@router.get("/", response_model=List[cerdo.CerdoResponse])
def leer_cerdos(corral: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Obtiene el inventario completo de cerdos. 
    Puedes escribir el nombre de un 'corral' para filtrar los resultados.
    """
    return repository.obtener_cerdos(db=db, corral=corral)

@router.get("/{cerdo_id}", response_model=cerdo.CerdoResponse)
def leer_cerdo_por_id(cerdo_id: int, db: Session = Depends(get_db)):
    """Obtiene los detalles de un cerdo específico."""
    db_cerdo = repository.obtener_cerdo_por_id(db, cerdo_id)
    if db_cerdo is None:
        raise HTTPException(status_code=404, detail="Cerdo no encontrado en la granja")
    return db_cerdo

@router.patch("/{cerdo_id}", response_model=cerdo.CerdoResponse)
def actualizar_datos_cerdo(cerdo_id: int, datos: cerdo.CerdoUpdate, db: Session = Depends(get_db)):
    """Actualiza los datos de un cerdo (Ej: Registrar un nuevo peso)."""
    db_cerdo = repository.actualizar_cerdo(db, cerdo_id, datos)
    if db_cerdo is None:
        raise HTTPException(status_code=404, detail="Cerdo no encontrado en la granja")
    return db_cerdo

@router.delete("/{cerdo_id}", status_code=status.HTTP_204_NO_CONTENT)
def borrar_cerdo(cerdo_id: int, db: Session = Depends(get_db)):
    """Elimina un cerdo del sistema."""
    db_cerdo = repository.eliminar_cerdo(db, cerdo_id)
    if db_cerdo is None:
        raise HTTPException(status_code=404, detail="Cerdo no encontrado en la granja")
    return None # El código 204 significa "Éxito, pero no hay nada que mostrar"

@router.post("/", response_model=cerdo.CerdoResponse)
def crear_cerdo(nuevo_cerdo: cerdo.CerdoCreate, db: Session = Depends(get_db)):
    """Registra un nuevo cerdo validando que el corral exista y tenga espacio."""
    
    # 1. Traemos la información del corral desde el Microservicio de Corrales
    datos_corral = corrales_client.verificar_corral_existe(nuevo_cerdo.corral)
    capacidad_maxima = datos_corral["capacidad_maxima"]
    
    # 2. Contamos cuántos cerdos hay ACTUALMENTE en ese corral (en el Inventario)
    cerdos_actuales = repository.contar_cerdos_por_corral(db, nuevo_cerdo.corral)
    
    # 3. LA VALIDACIÓN MAESTRA
    if cerdos_actuales >= capacidad_maxima:
        raise HTTPException(
            status_code=400, # 400 Bad Request: El usuario está pidiendo algo imposible
            detail=f"Hacinamiento evitado: El {nuevo_cerdo.corral} tiene una capacidad máxima de {capacidad_maxima} cerdos y ya está lleno."
        )
    
    # 4. Si hay espacio, guardamos el cerdo exitosamente
    return repository.registrar_cerdo(db=db, cerdo_in=nuevo_cerdo)