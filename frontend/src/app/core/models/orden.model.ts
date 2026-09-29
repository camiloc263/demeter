export type EtapaOrden = 'LEVANTE' | 'ENGORDE' | 'GESTACION' | 'LACTANCIA' | 'FINALIZACION';

export const ETAPAS_ORDEN: EtapaOrden[] = ['LEVANTE', 'ENGORDE', 'GESTACION', 'LACTANCIA', 'FINALIZACION'];

export interface SolicitudOrden {
  nombre_corral: string;
  numero_cerdos: number;
  peso_promedio_kg: number;
  etapa: EtapaOrden;
  temperatura_actual_c: number;
}

export interface RecetaLote {
  maiz_amarillo_kg: number;
  mogolla_fina_kg: number;
  mogolla_gruesa_kg: number;
  cal_agricola_kg: number;
  sal_mineral_kg: number;
  harina_pescado_kg: number;
  liquido_hidratacion_litros: number;
}

export interface OrdenTrabajo {
  id: number;
  codigo_orden: string;
  corral_objetivo: string;
  total_raciones_kg: number;
  receta_preparacion_lote: RecetaLote;
  instrucciones_sop: string[];
  estado: string;
  fecha_creacion: string;
}

export interface ConfirmacionOrden {
  operario_responsable: string;
  observaciones?: string;
}
