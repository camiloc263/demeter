import { Component, OnInit, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { CorralesService } from '../../core/services/corrales.service';
import { ToastService } from '../../shared/toast/toast.service';
import { Corral } from '../../core/models/corral.model';
import { ETAPAS_CORRAL } from '../../core/models/corral.model';

@Component({
  selector: 'app-corrales',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './corrales.component.html',
  styleUrl: './corrales.component.scss',
})
export class CorralesComponent implements OnInit {
  private svc = inject(CorralesService);
  private toast = inject(ToastService);
  private fb = inject(FormBuilder);

  readonly etapas = ETAPAS_CORRAL;

  corrales = signal<Corral[]>([]);
  cargando = signal(true);
  modalAbierto = signal(false);
  editando = signal<Corral | null>(null);
  guardando = signal(false);

  form = this.fb.nonNullable.group({
    nombre: ['', Validators.required],
    capacidad_maxima: [10, [Validators.required, Validators.min(1)]],
    ancho_m: [5, [Validators.required, Validators.min(0.1)]],
    largo_m: [5, [Validators.required, Validators.min(0.1)]],
    etapa: ['Engorde' as (typeof ETAPAS_CORRAL)[number], Validators.required],
  });

  ngOnInit(): void {
    this.cargar();
  }

  cargar(): void {
    this.cargando.set(true);
    this.svc.listar().subscribe({
      next: (lista) => {
        this.corrales.set(lista);
        this.cargando.set(false);
      },
      error: () => {
        this.toast.error('No se pudo cargar la lista de corrales.');
        this.cargando.set(false);
      },
    });
  }

  abrirNuevo(): void {
    this.editando.set(null);
    this.form.reset({ nombre: '', capacidad_maxima: 10, ancho_m: 5, largo_m: 5, etapa: 'Engorde' });
    this.modalAbierto.set(true);
  }

  abrirEditar(corral: Corral): void {
    this.editando.set(corral);
    this.form.reset({
      nombre: corral.nombre,
      capacidad_maxima: corral.capacidad_maxima,
      ancho_m: corral.ancho_m,
      largo_m: corral.largo_m,
      etapa: corral.etapa,
    });
    this.modalAbierto.set(true);
  }

  cerrarModal(): void {
    this.modalAbierto.set(false);
  }

  guardar(): void {
    if (this.form.invalid || this.guardando()) return;
    this.guardando.set(true);
    const datos = this.form.getRawValue();
    const enEdicion = this.editando();

    const peticion = enEdicion ? this.svc.actualizar(enEdicion.id, datos) : this.svc.crear(datos);

    peticion.subscribe({
      next: () => {
        this.toast.ok(enEdicion ? 'Corral actualizado.' : 'Corral creado.');
        this.guardando.set(false);
        this.modalAbierto.set(false);
        this.cargar();
      },
      error: (err) => {
        this.guardando.set(false);
        this.toast.error(err.error?.detail ?? 'No se pudo guardar el corral.');
      },
    });
  }

  eliminar(corral: Corral): void {
    if (!confirm(`¿Eliminar el corral "${corral.nombre}"? Esta acción no se puede deshacer.`)) return;

    this.svc.eliminar(corral.id).subscribe({
      next: () => {
        this.toast.ok('Corral eliminado.');
        this.cargar();
      },
      error: (err) => this.toast.error(err.error?.detail ?? 'No se pudo eliminar el corral.'),
    });
  }
}
