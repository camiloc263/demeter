export interface DatosEvaluacionNotificacion {
  nombre_corral: string;
  telefono_trabajador: string;
  hora_del_dia: number;
  temperatura_actual_c: number;
  horas_desde_ultima_comida: number;
  raciones_pendientes_kg: number;
}

export interface ResultadoNotificacion {
  estado: 'NOTIFICACION_ENVIADA' | 'EN_ESPERA';
  mensaje: string;
}

export interface AlertaDirecta {
  numero_telefono: string;
  corral: string;
  racion_kg: number;
  motivo_ia: string;
}
