import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API } from '../config/api.config';
import { AlertaDirecta } from '../models/notificacion.model';

@Injectable({ providedIn: 'root' })
export class MlWsService {
  private base = API.mlWs;

  constructor(private http: HttpClient) {}

  reenviar(payload: AlertaDirecta): Observable<{ status: string; detail: unknown }> {
    return this.http.post<{ status: string; detail: unknown }>(`${this.base}/send-notification`, payload);
  }
}
