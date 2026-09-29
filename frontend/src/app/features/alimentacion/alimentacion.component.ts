import { Component, OnInit, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { AlimentacionService } from '../../core/services/alimentacion.service';
import { CorralesService } from '../../core/services/corrales.service';
import { ToastService } from '../../shared/toast/toast.service';
import { RegistroAlimentacion } from '../../core/models/alimentacion.model';
import { Corral } from '../../core/models/corral.model';

@Component({
  selector: 'app-alimentacion',
  standalone: true,
  imports: [ReactiveFormsModule, DatePipe],
  templateUrl: './alimentacion.component.html',
  styleUrl: './alimentacion.component.scss',
})
export class AlimentacionComponent implements OnInit {
  private svc = inject(AlimentacionService);
  private corralesSvc = inject(CorralesService);
  private toast = inject(ToastService);
  private fb = inject(FormBuilder);

  registros = signal<RegistroAlimentacion[]>([]);
  corrales = signal<Corral[]>([]);
  cargando = signal(true);
  modalAbierto = signal(false);
  guardando = signal(false);

  form = this.fb.nonNullable.group({
    corral: ['', Validators.required],
    tipo_alimento: ['', Validators.required],
    cantidad_kg: [1, [Validators.required, Validators.min(0.1)]],
  });

  ngOnInit(): void {
    this.corralesSvc.listar().subscribe((c) => this.corrales.set(c));
    this.cargar();
  }

  cargar(): void {
    this.cargando.set(true);
    this.svc.listar().subscribe({
      next: (lista) => {
        this.registros.set(lista.sort((a, b) => b.fecha_hora.localeCompare(a.fecha_hora)));
        this.cargando.set(false);
      },
      error: () => {
        this.toast.error('No se pudo cargar el historial de alimentación.');
        this.cargando.set(false);
      },
    });
  }

  abrirNuevo(): void {
    this.form.reset({ corral: '', tipo_alimento: '', cantidad_kg: 1 });
    this.modalAbierto.set(true);
  }

  cerrarModal(): void {
    this.modalAbierto.set(false);
  }

  guardar(): void {
    if (this.form.invalid || this.guardando()) return;
    this.guardando.set(true);

    this.svc.crear(this.form.getRawValue()).subscribe({
      next: () => {
        this.toast.ok('Alimentación registrada.');
        this.guardando.set(false);
        this.modalAbierto.set(false);
        this.cargar();
      },
      error: (err) => {
        this.guardando.set(false);
        this.toast.error(err.error?.detail ?? 'No se pudo registrar la alimentación.');
      },
    });
  }

  eliminar(registro: RegistroAlimentacion): void {
    if (!confirm('¿Eliminar este registro de alimentación?')) return;

    this.svc.eliminar(registro.id).subscribe({
      next: () => {
        this.toast.ok('Registro eliminado.');
        this.cargar();
      },
      error: (err) => this.toast.error(err.error?.detail ?? 'No se pudo eliminar el registro.'),
    });
  }
}
