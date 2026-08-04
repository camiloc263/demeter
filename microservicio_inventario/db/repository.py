from sqlalchemy.orm import Session
from . import models
from schemas import cerdo

def registrar_cerdo(db: Session, cerdo_in: cerdo.CerdoCreate):
    """Toma los datos validados y los guarda en la base de datos."""
    # Convertimos el esquema de Pydantic al modelo de SQLAlchemy
    db_cerdo = models.CerdoORM(**cerdo_in.model_dump())
    
    db.add(db_cerdo)        # Lo preparamos para guardar
    db.commit()             # Guardamos los cambios físicamente
    db.refresh(db_cerdo)    # Actualizamos para obtener el ID generado
    
    return db_cerdo

def obtener_cerdos(db: Session, corral: str = None):
    """Devuelve la lista de todos los cerdos, filtrando por corral si se especifica."""
    if corral:
        # Si el usuario escribió un corral, filtramos la búsqueda
        return db.query(models.CerdoORM).filter(models.CerdoORM.corral == corral).all()
    
    # Si no especificó corral, devolvemos absolutamente todos
    return db.query(models.CerdoORM).all()

def obtener_cerdo_por_id(db: Session, cerdo_id: int):
    """Busca un cerdo específico usando su ID interno."""
    return db.query(models.CerdoORM).filter(models.CerdoORM.id == cerdo_id).first()

def actualizar_cerdo(db: Session, cerdo_id: int, datos_actualizados: cerdo.CerdoUpdate):
    """Actualiza solo los campos que el usuario haya enviado."""
    db_cerdo = obtener_cerdo_por_id(db, cerdo_id)
    
    if db_cerdo:
        # El truco exclude_unset=True ignora los campos que el usuario no envió
        datos_dict = datos_actualizados.model_dump(exclude_unset=True) 
        
        for clave, valor in datos_dict.items():
            setattr(db_cerdo, clave, valor) # Cambia el valor viejo por el nuevo
            
        db.commit()
        db.refresh(db_cerdo)
        
    return db_cerdo

def eliminar_cerdo(db: Session, cerdo_id: int):
    """Elimina permanentemente un cerdo de la base de datos."""
    db_cerdo = obtener_cerdo_por_id(db, cerdo_id)
    
    if db_cerdo:
        db.delete(db_cerdo)
        db.commit()
        
    return db_cerdo

def contar_cerdos_por_corral(db: Session, corral: str):
    """Cuenta rápidamente cuántos cerdos hay en un corral usando la base de datos."""
    return db.query(models.CerdoORM).filter(models.CerdoORM.corral == corral).count()