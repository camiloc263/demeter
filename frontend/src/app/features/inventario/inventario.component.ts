import { Component, OnInit, inject, signal } from '@angular/core';
import { FormBuilder, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { InventarioService } from '../../core/services/inventario.service';
import { CorralesService } from '../../core/services/corrales.service';
import { ToastService } from '../../shared/toast/toast.service';
import { Cerdo } from '../../core/models/cerdo.model';
import { Corral, ETAPAS_CORRAL } from '../../core/models/corral.model';

@Component({
  selector: 'app-inventario',
  standalone: true,
  imports: [ReactiveFormsModule, FormsModule],
  templateUrl: './inventario.component.html',
  styleUrl: './inventario.component.scss',
})
export class InventarioComponent implements OnInit {
  private svc = inject(InventarioService);
  private corralesSvc = inject(CorralesService);
  private toast = inject(ToastService);
  private fb = inject(FormBuilder);

  readonly etapas = ETAPAS_CORRAL;

  cerdos = signal<Cerdo[]>([]);
  corrales = signal<Corral[]>([]);
  cargando = signal(true);
  filtroCorral = signal('');
  modalAbierto = signal(false);
  editando = signal<Cerdo | null>(null);
  guardando = signal(false);

  form = this.fb.nonNullable.group({
    etiqueta: ['', Validators.required],
    raza: [''],
    fecha_nacimiento: ['', Validators.required],
    etapa: ['Engorde' as (typeof ETAPAS_CORRAL)[number], Validators.required],
    peso_kg: [20, [Validators.required, Validators.min(0.1)]],
    corral: ['', Validators.required],
    madre_etiqueta: [''],
  });

  ngOnInit(): void {
    this.corralesSvc.listar().subscribe((c) => this.corrales.set(c));
    this.cargar();
  }

  cargar(): void {
    this.cargando.set(true);
    this.svc.listar(this.filtroCorral() || undefined).subscribe({
      next: (lista) => {
        this.cerdos.set(lista);
        this.cargando.set(false);
      },
      error: () => {
        this.toast.error('No se pudo cargar el inventario.');
        this.cargando.set(false);
      },
    });
  }

  aplicarFiltro(corral: string): void {
    this.filtroCorral.set(corral);
    this.cargar();
  }

  abrirNuevo(): void {
    this.editando.set(null);
    this.form.reset({
      etiqueta: '',
      raza: '',
      fecha_nacimiento: '',
      etapa: 'Engorde',
      peso_kg: 20,
      corral: this.filtroCorral() || '',
      madre_etiqueta: '',
    });
    this.modalAbierto.set(true);
  }

  abrirEditar(cerdo: Cerdo): void {
    this.editando.set(cerdo);
    this.form.reset({
      etiqueta: cerdo.etiqueta,
      raza: cerdo.raza ?? '',
      fecha_nacimiento: cerdo.fecha_nacimiento,
      etapa: cerdo.etapa,
      peso_kg: cerdo.peso_kg,
      corral: cerdo.corral,
      madre_etiqueta: cerdo.madre_etiqueta ?? '',
    });
    this.modalAbierto.set(true);
  }

  cerrarModal(): void {
    this.modalAbierto.set(false);
  }

  guardar(): void {
    if (this.form.invalid || this.guardando()) return;
    this.guardando.set(true);
    const valores = this.form.getRawValue();
    const datos = {
      ...valores,
      raza: valores.raza || undefined,
      madre_etiqueta: valores.madre_etiqueta || undefined,
    };
    const enEdicion = this.editando();

    const peticion = enEdicion ? this.svc.actualizar(enEdicion.id, datos) : this.svc.crear(datos);

    peticion.subscribe({
      next: () => {
        this.toast.ok(enEdicion ? 'Cerdo actualizado.' : 'Cerdo registrado.');
        this.guardando.set(false);
        this.modalAbierto.set(false);
        this.cargar();
      },
      error: (err) => {
        this.guardando.set(false);
        this.toast.error(err.error?.detail ?? 'No se pudo guardar el registro.');
      },
    });
  }

  eliminar(cerdo: Cerdo): void {
    if (!confirm(`¿Eliminar el cerdo "${cerdo.etiqueta}"? Esta acción no se puede deshacer.`)) return;

    this.svc.eliminar(cerdo.id).subscribe({
      next: () => {
        this.toast.ok('Cerdo eliminado.');
        this.cargar();
      },
      error: (err) => this.toast.error(err.error?.detail ?? 'No se pudo eliminar el cerdo.'),
    });
  }
}
