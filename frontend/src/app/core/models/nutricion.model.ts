export interface DatosNutricion {
  edad_dias: number;
  peso_actual_kg: number;
  temperatura_c: number;
}

export interface PrediccionDieta {
  racion_recomendada_kg: number;
  costo_estimado_usd: number;
  analisis: string;
}

export interface RegistroComida {
  id: number;
  id_cerdo_rfid: string;
  corral: string;
  racion_servida_kg: number;
  fecha_hora: string;
}
