import { Component, inject } from '@angular/core';
import { Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { ToastComponent } from '../../shared/toast/toast.component';

interface NavItem {
  ruta: string;
  etiqueta: string;
  icono: string;
}

@Component({
  selector: 'app-shell',
  standalone: true,
  imports: [RouterLink, RouterLinkActive, RouterOutlet, ToastComponent],
  templateUrl: './shell.component.html',
  styleUrl: './shell.component.scss',
})
export class ShellComponent {
  private auth = inject(AuthService);
  private router = inject(Router);

  usuario = this.auth.usuarioActual;

  readonly nav: NavItem[] = [
    { ruta: '/dashboard', etiqueta: 'Panel', icono: '◧' },
    { ruta: '/corrales', etiqueta: 'Corrales', icono: '▦' },
    { ruta: '/inventario', etiqueta: 'Inventario', icono: '◍' },
    { ruta: '/alimentacion', etiqueta: 'Alimentación', icono: '◑' },
    { ruta: '/iot', etiqueta: 'Sensores', icono: '◈' },
    { ruta: '/ordenes', etiqueta: 'Órdenes de trabajo', icono: '▤' },
    { ruta: '/alimentacion-ia', etiqueta: 'Predicción IA', icono: '✦' },
    { ruta: '/clima', etiqueta: 'Clima', icono: '☁' },
    { ruta: '/notificaciones', etiqueta: 'Notificaciones', icono: '✉' },
    { ruta: '/ia-notificaciones', etiqueta: 'Decisión IA', icono: '⚙' },
    { ruta: '/ml-ws', etiqueta: 'Reenvío ML', icono: '⇄' },
  ];

  salir(): void {
    this.auth.logout();
    this.router.navigate(['/login']);
  }
}
