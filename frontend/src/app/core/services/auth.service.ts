import { Injectable, computed, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { API } from '../config/api.config';
import { LoginRequest, Rol, Token, UsuarioCreate, Usuario } from '../models/usuario.model';

const STORAGE_KEY = 'demeter.sesion';

interface SesionGuardada {
  token: string;
  rol: Rol;
  username: string;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private sesion = signal<SesionGuardada | null>(this.leerSesionGuardada());

  readonly estaAutenticado = computed(() => this.sesion() !== null);
  readonly usuarioActual = computed(() => this.sesion());
  readonly esAdministrador = computed(() => this.sesion()?.rol === 'administrador');

  constructor(private http: HttpClient) {}

  get token(): string | null {
    return this.sesion()?.token ?? null;
  }

  login(credenciales: LoginRequest): Observable<Token> {
    return this.http.post<Token>(`${API.usuarios}/usuarios/login`, credenciales).pipe(
      tap((respuesta) => {
        const sesion: SesionGuardada = {
          token: respuesta.access_token,
          rol: respuesta.rol,
          username: credenciales.username,
        };
        this.sesion.set(sesion);
        localStorage.setItem(STORAGE_KEY, JSON.stringify(sesion));
      }),
    );
  }

  registrar(datos: UsuarioCreate): Observable<Usuario> {
    return this.http.post<Usuario>(`${API.usuarios}/usuarios/`, datos);
  }

  logout(): void {
    this.sesion.set(null);
    localStorage.removeItem(STORAGE_KEY);
  }

  private leerSesionGuardada(): SesionGuardada | null {
    try {
      const crudo = localStorage.getItem(STORAGE_KEY);
      return crudo ? (JSON.parse(crudo) as SesionGuardada) : null;
    } catch {
      return null;
    }
  }
}
