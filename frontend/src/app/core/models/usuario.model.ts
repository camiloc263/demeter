export type Rol = 'administrador' | 'empleado';

export interface LoginRequest {
  username: string;
  password: string;
}

export interface Token {
  access_token: string;
  token_type: string;
  rol: Rol;
  refresh_token?: string;
}

export interface Usuario {
  id: number;
  username: string;
  rol: Rol;
  activo: boolean;
}

export interface UsuarioCreate {
  username: string;
  rol: Rol;
  password: string;
  activo?: boolean;
}
