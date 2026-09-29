export interface LecturaIot {
  id: number;
  corral: string;
  temperatura_c: number;
  humedad_pct: number;
  fecha_hora: string;
}

export interface LecturaIotCreate {
  corral: string;
  temperatura_c: number;
  humedad_pct: number;
}
