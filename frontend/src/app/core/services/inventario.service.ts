import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { API } from '../config/api.config';
import { Cerdo, CerdoCreate, CerdoUpdate } from '../models/cerdo.model';

@Injectable({ providedIn: 'root' })
export class InventarioService {
  private base = `${API.inventario}/cerdos`;

  constructor(private http: HttpClient) {}

  listar(corral?: string): Observable<Cerdo[]> {
    let params = new HttpParams();
    if (corral) params = params.set('corral', corral);
    return this.http.get<Cerdo[]>(`${this.base}/`, { params });
  }

  /** El backend no tiene un endpoint de búsqueda por etiqueta, así que se
   * trae la lista completa y se filtra en el cliente — aceptable para el
   * tamaño de inventario de una granja. */
  buscarPorEtiqueta(etiqueta: string): Observable<Cerdo | undefined> {
    return this.listar().pipe(map((lista) => lista.find((c) => c.etiqueta === etiqueta)));
  }

  crear(datos: CerdoCreate): Observable<Cerdo> {
    return this.http.post<Cerdo>(`${this.base}/`, datos);
  }

  actualizar(id: number, datos: CerdoUpdate): Observable<Cerdo> {
    return this.http.patch<Cerdo>(`${this.base}/${id}`, datos);
  }

  eliminar(id: number): Observable<void> {
    return this.http.delete<void>(`${this.base}/${id}`);
  }
}
