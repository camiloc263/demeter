import { Injectable, signal } from '@angular/core';

export interface Toast {
  id: number;
  tipo: 'ok' | 'error';
  mensaje: string;
}

@Injectable({ providedIn: 'root' })
export class ToastService {
  private contador = 0;
  readonly toasts = signal<Toast[]>([]);

  ok(mensaje: string): void {
    this.mostrar('ok', mensaje);
  }

  error(mensaje: string): void {
    this.mostrar('error', mensaje);
  }

  cerrar(id: number): void {
    this.toasts.update((lista) => lista.filter((t) => t.id !== id));
  }

  private mostrar(tipo: Toast['tipo'], mensaje: string): void {
    const id = ++this.contador;
    this.toasts.update((lista) => [...lista, { id, tipo, mensaje }]);
    setTimeout(() => this.cerrar(id), 4500);
  }
}
