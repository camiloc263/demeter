import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API } from '../config/api.config';
import { LecturaIot } from '../models/lectura.model';

@Injectable({ providedIn: 'root' })
export class IotService {
  private base = `${API.iot}/iot`;

  constructor(private http: HttpClient) {}

  lecturasPorCorral(corral: string, limite = 10): Observable<LecturaIot[]> {
    const params = new HttpParams().set('limite', limite);
    return this.http.get<LecturaIot[]>(`${this.base}/corral/${encodeURIComponent(corral)}`, { params });
  }
}
