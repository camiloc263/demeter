import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API } from '../config/api.config';
import { DecisionAlerta, EvaluacionAlertaInput } from '../models/decision-alerta.model';

@Injectable({ providedIn: 'root' })
export class IaNotificacionesService {
  private base = API.iaNotificaciones;

  constructor(private http: HttpClient) {}

  evaluarYNotificar(payload: EvaluacionAlertaInput): Observable<DecisionAlerta> {
    return this.http.post<DecisionAlerta>(`${this.base}/evaluar-y-notificar`, payload);
  }
}
