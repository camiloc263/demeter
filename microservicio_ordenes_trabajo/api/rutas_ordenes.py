from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import json
import uuid
import datetime

from ..db.database import get_db
from ..db import models
from ..schemas import ordenes
from demeter_core.auth import obtener_usuario_actual

router = APIRouter(prefix="/ordenes", tags=["Gestión de Alimentación Manual"])

# Matriz de Formulación del Manual Operativo (Gramose por cada 1 Kg de alimento seco)
RECETARIO_SOP = {
    "LEVANTE": {"maiz": 311.6, "m_fina": 498.4, "m_gruesa": 150.0, "cal": 10.0, "sal": 10.0, "pescado": 30.0, "liquido": 2.25},
    "ENGORDE": {"maiz": 400.0, "m_fina": 540.0, "m_gruesa": 0.0, "cal": 10.0, "sal": 10.0, "pescado": 30.0, "liquido": 2.75},
    "GESTACION": {"maiz": 100.0, "m_fina": 0.0, "m_gruesa": 850.0, "cal": 30.0, "sal": 10.0, "pescado": 10.0, "liquido": 2.25},
    "LACTANCIA": {"maiz": 300.0, "m_fina": 520.0, "m_gruesa": 130.0, "cal": 10.0, "sal": 10.0, "pescado": 30.0, "liquido": 3.25},
    "FINALIZACION": {"maiz": 500.0, "m_fina": 370.0, "m_gruesa": 110.0, "cal": 10.0, "sal": 10.0, "pescado": 0.0, "liquido": 2.75}
}

@router.post("/generar", response_model=ordenes.OrdenRespuesta)
def generar_orden_trabajo(
    solicitud: ordenes.SolicitudOrden,
    db: Session = Depends(get_db),
    _usuario=Depends(obtener_usuario_actual),
):
    """Calcula la mezcla según el SOP y genera una Orden de Trabajo persistente."""
    
    # 1. Ración base estimada (4% del peso vivo ajustado por temperatura)
    estres_calorico = max(0, (solicitud.temperatura_actual_c - 22)) / 100.0
    racion_individual_kg = (solicitud.peso_promedio_kg * 0.04) * (1 - estres_calorico)
    
    total_lote_kg = racion_individual_kg * solicitud.numero_cerdos
    
    # 2. Formulación del lote
    base = RECETARIO_SOP[solicitud.etapa]
    receta_dict = {
        "maiz_amarillo_kg": round((base["maiz"] * total_lote_kg) / 1000, 2),
        "mogolla_fina_kg": round((base["m_fina"] * total_lote_kg) / 1000, 2),
        "mogolla_gruesa_kg": round((base["m_gruesa"] * total_lote_kg) / 1000, 2),
        "cal_agricola_kg": round((base["cal"] * total_lote_kg) / 1000, 2),
        "sal_mineral_kg": round((base["sal"] * total_lote_kg) / 1000, 2),
        "harina_pescado_kg": round((base["pescado"] * total_lote_kg) / 1000, 2) if solicitud.etapa != "FINALIZACION" else 0.0,
        "liquido_hidratacion_litros": round(base["liquido"] * total_lote_kg, 2)
    }
    
    # 3. Instrucciones estandarizadas del SOP
    instrucciones = [
        "1. PESAJE ESTRICTO: Usar báscula calibrada y restar el peso del balde/tarra.",
        "2. MEZCLADO EN SECO: Mezclar sólidos uniformemente ANTES de añadir líquido.",
        "3. HIDRATACIÓN EN CANOA: Añadir líquido directamente en la canoa al momento de servir."
    ]
    
    if solicitud.peso_promedio_kg >= 110:
        total_lote_kg = 0.0 # Cortar alimento por pre-faena
        instrucciones.insert(0, "🛑 ALERTA PRE-FAENA: Suspender alimento sólido y líquido 12 a 18h antes del transporte.")
    elif solicitud.etapa == "FINALIZACION":
        instrucciones.insert(0, "⚠️ CALIDAD DE CARNE: Uso de Harina de Pescado estrictamente BLOQUEADO.")

    # 4. Guardar la orden en la base de datos
    codigo_unico = f"ORD-{datetime.datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"
    
    nueva_orden = models.OrdenTrabajoORM(
        codigo_orden=codigo_unico,
        corral_objetivo=solicitud.nombre_corral,
        total_raciones_kg=round(total_lote_kg, 2),
        receta_json=json.dumps(receta_dict),
        instrucciones_json=json.dumps(instrucciones),
        estado="PENDIENTE"
    )
    
    db.add(nueva_orden)
    db.commit()
    db.refresh(nueva_orden)
    
    return ordenes.OrdenRespuesta(
        id=nueva_orden.id,
        codigo_orden=nueva_orden.codigo_orden,
        corral_objetivo=nueva_orden.corral_objetivo,
        total_raciones_kg=nueva_orden.total_raciones_kg,
        receta_preparacion_lote=ordenes.RecetaLote(**receta_dict),
        instrucciones_sop=instrucciones,
        estado=nueva_orden.estado,
        fecha_creacion=nueva_orden.fecha_creacion
    )

@router.put("/completar/{codigo_orden}")
def completar_orden(
    codigo_orden: str,
    datos: ordenes.ConfirmacionOrden,
    db: Session = Depends(get_db),
    _usuario=Depends(obtener_usuario_actual),
):
    """El operario confirma que la orden de mezcla y servido fue ejecutada en la canoa."""
    orden = db.query(models.OrdenTrabajoORM).filter(models.OrdenTrabajoORM.codigo_orden == codigo_orden).first()
    
    if not orden:
        raise HTTPException(status_code=404, detail="Orden de trabajo no encontrada.")
        
    if orden.estado == "COMPLETADA":
        raise HTTPException(status_code=400, detail="Esta orden ya fue marcada como completada anteriormente.")
        
    orden.estado = "COMPLETADA"
    orden.operario_responsable = datos.operario_responsable
    orden.observaciones = datos.observaciones
    orden.fecha_completado = datetime.datetime.utcnow()
    
    db.commit()
    return {"mensaje": f"✅ Orden {codigo_orden} completada exitosamente por {datos.operario_responsable}."}

@router.get("/pendientes", response_model=List[ordenes.OrdenRespuesta])
def listar_ordenes_pendientes(db: Session = Depends(get_db)):
    """Obtiene la lista de órdenes activas que el personal de campo debe preparar."""
    ordenes_orm = db.query(models.OrdenTrabajoORM).filter(models.OrdenTrabajoORM.estado == "PENDIENTE").all()
    
    resultado = []
    for ord_orm in ordenes_orm:
        resultado.append(ordenes.OrdenRespuesta(
            id=ord_orm.id,
            codigo_orden=ord_orm.codigo_orden,
            corral_objetivo=ord_orm.corral_objetivo,
            total_raciones_kg=ord_orm.total_raciones_kg,
            receta_preparacion_lote=ordenes.RecetaLote(**json.loads(ord_orm.receta_json)),
            instrucciones_sop=json.loads(ord_orm.instrucciones_json),
            estado=ord_orm.estado,
            fecha_creacion=ord_orm.fecha_creacion
        ))
    return resultado