import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API } from '../config/api.config';
import { RegistroAlimentacion, RegistroAlimentacionCreate } from '../models/alimentacion.model';

@Injectable({ providedIn: 'root' })
export class AlimentacionService {
  private base = `${API.alimentacion}/alimentacion`;

  constructor(private http: HttpClient) {}

  listar(corral?: string): Observable<RegistroAlimentacion[]> {
    let params = new HttpParams();
    if (corral) params = params.set('corral', corral);
    return this.http.get<RegistroAlimentacion[]>(`${this.base}/`, { params });
  }

  crear(datos: RegistroAlimentacionCreate): Observable<RegistroAlimentacion> {
    return this.http.post<RegistroAlimentacion>(`${this.base}/`, datos);
  }

  eliminar(id: number): Observable<void> {
    return this.http.delete<void>(`${this.base}/${id}`);
  }
}
