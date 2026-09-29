export interface RegistroAlimentacion {
  id: number;
  corral: string;
  tipo_alimento: string;
  cantidad_kg: number;
  fecha_hora: string;
}

export interface RegistroAlimentacionCreate {
  corral: string;
  tipo_alimento: string;
  cantidad_kg: number;
}
