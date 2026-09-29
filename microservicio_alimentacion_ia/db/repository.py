from sqlalchemy.orm import Session

from . import models
from ..schemas import nutricion


def registrar_comida(db: Session, comida: nutricion.RegistroComidaCreate):
    """Guarda un evento de comedero RFID: qué cerdo comió, dónde y cuánto."""
    db_registro = models.RegistroComidaORM(**comida.model_dump())
    db.add(db_registro)
    db.commit()
    db.refresh(db_registro)
    return db_registro


def obtener_historial_cerdo(db: Session, id_cerdo_rfid: str):
    """Devuelve el historial de comedero de un cerdo, más reciente primero."""
    return (
        db.query(models.RegistroComidaORM)
        .filter(models.RegistroComidaORM.id_cerdo_rfid == id_cerdo_rfid)
        .order_by(models.RegistroComidaORM.fecha_hora.desc())
        .all()
    )
