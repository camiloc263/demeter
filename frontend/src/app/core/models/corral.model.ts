export const ETAPAS_CORRAL = [
  'Gestación',
  'Paridas',
  'Engorde',
  'Finalización',
  'Levante',
  'Inicio',
  'Preinicio',
] as const;

export type EtapaCorral = (typeof ETAPAS_CORRAL)[number];

export interface Corral {
  id: number;
  nombre: string;
  capacidad_maxima: number;
  ancho_m: number;
  largo_m: number;
  area_m2: number;
  etapa: EtapaCorral;
}

export interface CorralCreate {
  nombre: string;
  capacidad_maxima: number;
  ancho_m: number;
  largo_m: number;
  etapa: EtapaCorral;
}

export type CorralUpdate = Partial<CorralCreate>;
