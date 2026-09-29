import { EtapaCorral } from './corral.model';

export interface Cerdo {
  id: number;
  etiqueta: string;
  raza?: string | null;
  fecha_nacimiento: string; // YYYY-MM-DD
  etapa: EtapaCorral;
  madre_etiqueta?: string | null;
  peso_kg: number;
  corral: string;
}

export interface CerdoCreate {
  etiqueta: string;
  raza?: string;
  fecha_nacimiento: string;
  etapa: EtapaCorral;
  madre_etiqueta?: string;
  peso_kg: number;
  corral: string;
}

export type CerdoUpdate = Partial<CerdoCreate>;
