import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API } from '../config/api.config';
import { Corral, CorralCreate, CorralUpdate } from '../models/corral.model';

@Injectable({ providedIn: 'root' })
export class CorralesService {
  private base = `${API.corrales}/corrales`;

  constructor(private http: HttpClient) {}

  listar(): Observable<Corral[]> {
    return this.http.get<Corral[]>(`${this.base}/`);
  }

  crear(datos: CorralCreate): Observable<Corral> {
    return this.http.post<Corral>(`${this.base}/`, datos);
  }

  actualizar(id: number, datos: CorralUpdate): Observable<Corral> {
    return this.http.patch<Corral>(`${this.base}/${id}`, datos);
  }

  eliminar(id: number): Observable<void> {
    return this.http.delete<void>(`${this.base}/${id}`);
  }
}
