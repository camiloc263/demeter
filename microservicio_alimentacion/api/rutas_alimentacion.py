from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from ..db.database import get_db
from ..schemas import registro
from ..db import repository
from ..services import inventario_client
from fastapi import APIRouter, Depends, HTTPException, status
from demeter_core.auth import obtener_usuario_actual

router = APIRouter(prefix="/alimentacion", tags=["Gestión de Alimentación"])

@router.post("/", response_model=registro.RegistroResponse)
def registrar_alimento(
    nuevo_registro: registro.RegistroCreate,
    db: Session = Depends(get_db),
    _usuario=Depends(obtener_usuario_actual),
):
    """Registra una ración de comida entregada a un corral."""


# 1. PASO DE SEGURIDAD: Preguntamos al Inventario si el corral es válido
    inventario_client.verificar_corral_existe(nuevo_registro.corral)
    
    # 2. Si la validación no arroja errores, procedemos a guardar en la base de datos
    return repository.registrar_consumo(db, nuevo_registro)

@router.get("/", response_model=List[registro.RegistroResponse])
def leer_registros(corral: Optional[str] = None, db: Session = Depends(get_db)):
    """Obtiene el historial de alimentación. Puedes filtrar por corral."""
    return repository.obtener_registros(db, corral)

@router.get("/{registro_id}", response_model=registro.RegistroResponse)
def leer_registro_por_id(registro_id: int, db: Session = Depends(get_db)):
    """Obtiene los detalles de un registro de comida específico."""
    db_registro = repository.obtener_registro_por_id(db, registro_id)
    if db_registro is None:
        raise HTTPException(status_code=404, detail="Registro de alimentación no encontrado.")
    return db_registro

@router.patch("/{registro_id}", response_model=registro.RegistroResponse)
def corregir_registro(
    registro_id: int,
    datos: registro.RegistroUpdate,
    db: Session = Depends(get_db),
    _usuario=Depends(obtener_usuario_actual),
):
    """Corrige un registro (Ej: si el operario anotó mal los kilos o el corral)."""
    
    # REGLA DE NEGOCIO: Si el usuario intenta cambiar el corral, validamos que el nuevo corral exista
    if datos.corral:
        inventario_client.verificar_corral_existe(datos.corral)
        
    db_registro = repository.actualizar_registro(db, registro_id, datos)
    if db_registro is None:
        raise HTTPException(status_code=404, detail="Registro de alimentación no encontrado.")
    return db_registro

@router.delete("/{registro_id}", status_code=status.HTTP_204_NO_CONTENT)
def borrar_registro(
    registro_id: int,
    db: Session = Depends(get_db),
    _usuario=Depends(obtener_usuario_actual),
):
    """Elimina un registro de comida del sistema."""
    db_registro = repository.eliminar_registro(db, registro_id)
    if db_registro is None:
        raise HTTPException(status_code=404, detail="Registro de alimentación no encontrado.")
    return None