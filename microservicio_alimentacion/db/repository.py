from sqlalchemy.orm import Session
from db import models
from schemas import registro

def registrar_consumo(db: Session, registro_in: registro.RegistroCreate):
    db_registro = models.RegistroAlimentacionORM(**registro_in.model_dump())
    db.add(db_registro)
    db.commit()
    db.refresh(db_registro)
    return db_registro

def obtener_registros(db: Session, corral: str = None):
    if corral:
        return db.query(models.RegistroAlimentacionORM).filter(models.RegistroAlimentacionORM.corral == corral).all()
    return db.query(models.RegistroAlimentacionORM).all()

def obtener_registro_por_id(db: Session, registro_id: int):
    """Busca un registro de alimentación específico por su ID."""
    return db.query(models.RegistroAlimentacionORM).filter(models.RegistroAlimentacionORM.id == registro_id).first()

def actualizar_registro(db: Session, registro_id: int, datos_actualizados: registro.RegistroUpdate):
    """Actualiza solo los campos que el usuario envíe para corregir el registro."""
    db_registro = obtener_registro_por_id(db, registro_id)
    
    if db_registro:
        # Extraemos solo los datos que el usuario quiere cambiar
        datos_dict = datos_actualizados.model_dump(exclude_unset=True) 
        
        for clave, valor in datos_dict.items():
            setattr(db_registro, clave, valor) # Reemplazamos el valor viejo
            
        db.commit()
        db.refresh(db_registro)
        
    return db_registro

def eliminar_registro(db: Session, registro_id: int):
    """Elimina permanentemente un registro de alimentación."""
    db_registro = obtener_registro_por_id(db, registro_id)
    
    if db_registro:
        db.delete(db_registro)
        db.commit()
        
    return db_registro