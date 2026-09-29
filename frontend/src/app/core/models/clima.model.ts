export interface CoordenadasGranja {
  nombre_granja: string;
  latitud: number;
  longitud: number;
  peso_promedio_kg?: number;
}

export interface RegistroClima {
  id: number;
  nombre_granja: string;
  latitud: number;
  longitud: number;
  temperatura_c: number;
  humedad_pct: number;
  estado_riesgo: string | null;
  mensaje_ia: string | null;
  certeza_ia: number | null;
  fecha_registro: string;
}
