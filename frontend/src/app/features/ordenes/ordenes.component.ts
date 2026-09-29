import { Component, OnInit, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { OrdenesService } from '../../core/services/ordenes.service';
import { CorralesService } from '../../core/services/corrales.service';
import { ToastService } from '../../shared/toast/toast.service';
import { ETAPAS_ORDEN, EtapaOrden, OrdenTrabajo } from '../../core/models/orden.model';
import { Corral } from '../../core/models/corral.model';

@Component({
  selector: 'app-ordenes',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './ordenes.component.html',
  styleUrl: './ordenes.component.scss',
})
export class OrdenesComponent implements OnInit {
  private svc = inject(OrdenesService);
  private corralesSvc = inject(CorralesService);
  private toast = inject(ToastService);
  private fb = inject(FormBuilder);

  readonly etapas = ETAPAS_ORDEN;

  ordenes = signal<OrdenTrabajo[]>([]);
  corrales = signal<Corral[]>([]);
  cargando = signal(true);
  modalAbierto = signal(false);
  detalle = signal<OrdenTrabajo | null>(null);
  guardando = signal(false);
  completando = signal<number | null>(null);

  form = this.fb.nonNullable.group({
    nombre_corral: ['', Validators.required],
    numero_cerdos: [10, [Validators.required, Validators.min(1)]],
    peso_promedio_kg: [40, [Validators.required, Validators.min(1)]],
    etapa: ['ENGORDE' as EtapaOrden, Validators.required],
    temperatura_actual_c: [24, Validators.required],
  });

  operarioForm = this.fb.nonNullable.group({
    operario_responsable: ['', Validators.required],
    observaciones: [''],
  });

  ngOnInit(): void {
    this.corralesSvc.listar().subscribe((c) => this.corrales.set(c));
    this.cargar();
  }

  cargar(): void {
    this.cargando.set(true);
    this.svc.pendientes().subscribe({
      next: (lista) => {
        this.ordenes.set(lista);
        this.cargando.set(false);
      },
      error: () => {
        this.toast.error('No se pudo cargar las órdenes de trabajo.');
        this.cargando.set(false);
      },
    });
  }

  abrirNuevo(): void {
    this.form.reset({ nombre_corral: '', numero_cerdos: 10, peso_promedio_kg: 40, etapa: 'ENGORDE', temperatura_actual_c: 24 });
    this.modalAbierto.set(true);
  }

  cerrarModal(): void {
    this.modalAbierto.set(false);
  }

  generar(): void {
    if (this.form.invalid || this.guardando()) return;
    this.guardando.set(true);

    this.svc.generar(this.form.getRawValue()).subscribe({
      next: () => {
        this.toast.ok('Orden de trabajo generada.');
        this.guardando.set(false);
        this.modalAbierto.set(false);
        this.cargar();
      },
      error: (err) => {
        this.guardando.set(false);
        this.toast.error(err.error?.detail ?? 'No se pudo generar la orden.');
      },
    });
  }

  verDetalle(orden: OrdenTrabajo): void {
    this.detalle.set(orden);
    this.operarioForm.reset({ operario_responsable: '', observaciones: '' });
  }

  cerrarDetalle(): void {
    this.detalle.set(null);
  }

  completar(): void {
    const orden = this.detalle();
    if (!orden || this.operarioForm.invalid) return;

    this.completando.set(orden.id);
    this.svc.completar(orden.codigo_orden, this.operarioForm.getRawValue()).subscribe({
      next: () => {
        this.toast.ok(`Orden ${orden.codigo_orden} marcada como completada.`);
        this.completando.set(null);
        this.detalle.set(null);
        this.cargar();
      },
      error: (err) => {
        this.completando.set(null);
        this.toast.error(err.error?.detail ?? 'No se pudo completar la orden.');
      },
    });
  }
}
