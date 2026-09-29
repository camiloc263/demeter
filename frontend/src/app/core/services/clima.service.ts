import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API } from '../config/api.config';
import { CoordenadasGranja, RegistroClima } from '../models/clima.model';

@Injectable({ providedIn: 'root' })
export class ClimaService {
  private base = `${API.clima}/clima_externo`;

  constructor(private http: HttpClient) {}

  consultarYGuardar(datos: CoordenadasGranja): Observable<RegistroClima> {
    return this.http.post<RegistroClima>(`${this.base}/consultar_y_guardar`, datos);
  }

  historial(nombreGranja: string): Observable<RegistroClima[]> {
    return this.http.get<RegistroClima[]>(`${this.base}/historial/${encodeURIComponent(nombreGranja)}`);
  }
}
