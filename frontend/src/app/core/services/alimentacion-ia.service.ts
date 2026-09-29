import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API } from '../config/api.config';
import { DatosNutricion, PrediccionDieta, RegistroComida } from '../models/nutricion.model';

@Injectable({ providedIn: 'root' })
export class AlimentacionIaService {
  private base = `${API.alimentacionIa}/alimentacion`;

  constructor(private http: HttpClient) {}

  predecirDieta(datos: DatosNutricion): Observable<PrediccionDieta> {
    return this.http.post<PrediccionDieta>(`${this.base}/predecir_dieta`, datos);
  }

  historialCerdo(rfid: string): Observable<RegistroComida[]> {
    return this.http.get<RegistroComida[]>(`${this.base}/historial/${encodeURIComponent(rfid)}`);
  }
}
