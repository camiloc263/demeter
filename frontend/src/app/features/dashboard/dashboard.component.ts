import { Component, OnInit, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';
import { CorralesService } from '../../core/services/corrales.service';
import { InventarioService } from '../../core/services/inventario.service';
import { OrdenesService } from '../../core/services/ordenes.service';
import { AuthService } from '../../core/services/auth.service';

interface Resumen {
  corrales: number;
  cerdos: number;
  ordenesPendientes: number;
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss',
})
export class DashboardComponent implements OnInit {
  private corralesSvc = inject(CorralesService);
  private inventarioSvc = inject(InventarioService);
  private ordenesSvc = inject(OrdenesService);
  auth = inject(AuthService);

  cargando = signal(true);
  resumen = signal<Resumen>({ corrales: 0, cerdos: 0, ordenesPendientes: 0 });
  errores = signal<string[]>([]);

  ngOnInit(): void {
    const errores: string[] = [];

    forkJoin({
      corrales: this.corralesSvc.listar(),
      cerdos: this.inventarioSvc.listar(),
      ordenes: this.ordenesSvc.pendientes(),
    }).subscribe({
      next: ({ corrales, cerdos, ordenes }) => {
        this.resumen.set({ corrales: corrales.length, cerdos: cerdos.length, ordenesPendientes: ordenes.length });
        this.cargando.set(false);
      },
      error: () => {
        errores.push('No se pudo cargar el resumen completo — revisa que corrales, inventario y órdenes de trabajo estén corriendo.');
        this.errores.set(errores);
        this.cargando.set(false);
      },
    });
  }
}
