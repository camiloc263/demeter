export interface EvaluacionAlertaInput {
  datos_clima: {
    temperatura_c: number;
    humedad_pct: number;
    peso_promedio_kg: number;
  };
  numero_telefono: string;
  corral: string;
}

export type AccionDecision = 'OMITIR_NOTIFICACION' | 'NOTIFICAR_EMAIL' | 'NOTIFICAR_WHATSAPP_URGENTE' | 'DESCONOCIDO';

export interface DecisionAlerta {
  codigo_decision: number;
  accion: AccionDecision;
  certeza: number;
  despacho_automatico: unknown;
}
