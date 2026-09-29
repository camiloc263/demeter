import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API } from '../config/api.config';
import { AlertaDirecta, DatosEvaluacionNotificacion, ResultadoNotificacion } from '../models/notificacion.model';

@Injectable({ providedIn: 'root' })
export class NotificacionesService {
  private base = API.notificaciones;

  constructor(private http: HttpClient) {}

  evaluar(datos: DatosEvaluacionNotificacion): Observable<ResultadoNotificacion> {
    return this.http.post<ResultadoNotificacion>(`${this.base}/evaluar_notificacion`, datos);
  }

  notificarDirecto(payload: AlertaDirecta): Observable<ResultadoNotificacion> {
    return this.http.post<ResultadoNotificacion>(`${this.base}/notificar`, payload);
  }
}
