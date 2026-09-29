from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..db.database import get_db
from ..schemas import cerdo
from ..db import repository
from ..services import corrales_client
from ..db import models
from demeter_core.auth import obtener_usuario_actual


# Creamos un "Router" para agrupar todas las rutas de los cerdos
router = APIRouter(prefix="/cerdos", tags=["Inventario de Cerdos"])

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
def actualizar_datos_cerdo(
    cerdo_id: int,
    datos: cerdo.CerdoUpdate,
    db: Session = Depends(get_db),
    _usuario=Depends(obtener_usuario_actual),
):
    """Actualiza los datos de un cerdo (Ej: Registrar un nuevo peso)."""
    db_cerdo = repository.actualizar_cerdo(db, cerdo_id, datos)
    if db_cerdo is None:
        raise HTTPException(status_code=404, detail="Cerdo no encontrado en la granja")
    return db_cerdo

@router.delete("/{cerdo_id}", status_code=status.HTTP_204_NO_CONTENT)
def borrar_cerdo(
    cerdo_id: int,
    db: Session = Depends(get_db),
    _usuario=Depends(obtener_usuario_actual),
):
    """Elimina un cerdo del sistema."""
    db_cerdo = repository.eliminar_cerdo(db, cerdo_id)
    if db_cerdo is None:
        raise HTTPException(status_code=404, detail="Cerdo no encontrado en la granja")
    return None # El código 204 significa "Éxito, pero no hay nada que mostrar"

@router.post("/", response_model=cerdo.CerdoResponse)
def crear_cerdo(
    nuevo_cerdo: cerdo.CerdoCreate,
    db: Session = Depends(get_db),
    _usuario=Depends(obtener_usuario_actual),
):
    """Registra un nuevo cerdo validando espacio y etapa del corral."""
    
    # 1. Traemos la información del corral (¡Aquí viene la etapa del corral!)
    datos_corral = corrales_client.verificar_corral_existe(nuevo_cerdo.corral)
    capacidad_maxima = datos_corral["capacidad_maxima"]
    etapa_corral = datos_corral.get("etapa") # Obtenemos la etapa
    
    # 2. VALIDACIÓN DE ETAPA (La nueva regla de negocio)
    if nuevo_cerdo.etapa.value != etapa_corral:
        raise HTTPException(
            status_code=400,
            detail=f"Incompatibilidad: Estás intentando meter un cerdo de '{nuevo_cerdo.etapa.value}' en un corral diseñado para '{etapa_corral}'."
        )
    
    # 3. Contamos los cerdos actuales
    cerdos_actuales = repository.contar_cerdos_por_corral(db, nuevo_cerdo.corral)
    
    # 4. VALIDACIÓN DE HACINAMIENTO
    if cerdos_actuales >= capacidad_maxima:
        raise HTTPException(
            status_code=400,
            detail=f"Hacinamiento evitado: El {nuevo_cerdo.corral} ya está lleno."
        )
    
    # Si todo está bien, guardamos
    return repository.registrar_cerdo(db=db, cerdo_in=nuevo_cerdo)

@router.get("/madre/{etiqueta_madre}/lechones", response_model=List[cerdo.CerdoResponse])
def obtener_camada_de_cerda(etiqueta_madre: str, db: Session = Depends(get_db)):
    """Devuelve la lista de todos los lechones que pertenecen a una madre específica."""
    
    lechones = db.query(models.CerdoORM).filter(models.CerdoORM.madre_etiqueta == etiqueta_madre).all()
    
    if not lechones:
        raise HTTPException(status_code=404, detail=f"No se encontraron lechones registrados para la madre {etiqueta_madre}")
        
    return lechones