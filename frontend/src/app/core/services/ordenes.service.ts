import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API } from '../config/api.config';
import { ConfirmacionOrden, OrdenTrabajo, SolicitudOrden } from '../models/orden.model';

@Injectable({ providedIn: 'root' })
export class OrdenesService {
  private base = `${API.ordenes}/ordenes`;

  constructor(private http: HttpClient) {}

  pendientes(): Observable<OrdenTrabajo[]> {
    return this.http.get<OrdenTrabajo[]>(`${this.base}/pendientes`);
  }

  generar(datos: SolicitudOrden): Observable<OrdenTrabajo> {
    return this.http.post<OrdenTrabajo>(`${this.base}/generar`, datos);
  }

  completar(codigo: string, datos: ConfirmacionOrden): Observable<OrdenTrabajo> {
    return this.http.put<OrdenTrabajo>(`${this.base}/completar/${encodeURIComponent(codigo)}`, datos);
  }
}
