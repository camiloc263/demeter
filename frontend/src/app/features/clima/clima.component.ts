import { Component, inject, signal } from '@angular/core';
import { DatePipe, NgClass } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ClimaService } from '../../core/services/clima.service';
import { ToastService } from '../../shared/toast/toast.service';
import { RegistroClima } from '../../core/models/clima.model';

@Component({
  selector: 'app-clima',
  standalone: true,
  imports: [ReactiveFormsModule, DatePipe, NgClass],
  templateUrl: './clima.component.html',
  styleUrl: './clima.component.scss',
})
export class ClimaComponent {
  private svc = inject(ClimaService);
  private toast = inject(ToastService);
  private fb = inject(FormBuilder);

  consultando = signal(false);
  ultimoResultado = signal<RegistroClima | null>(null);
  historial = signal<RegistroClima[]>([]);
  cargandoHistorial = signal(false);

  form = this.fb.nonNullable.group({
    nombre_granja: ['', Validators.required],
    latitud: [4.65, [Validators.required, Validators.min(-90), Validators.max(90)]],
    longitud: [-74.1, [Validators.required, Validators.min(-180), Validators.max(180)]],
    peso_promedio_kg: [100],
  });

  consultar(): void {
    if (this.form.invalid || this.consultando()) return;
    this.consultando.set(true);
    this.ultimoResultado.set(null);

    this.svc.consultarYGuardar(this.form.getRawValue()).subscribe({
      next: (resultado) => {
        this.ultimoResultado.set(resultado);
        this.consultando.set(false);
        this.toast.ok('Clima consultado y guardado.');
        this.cargarHistorial();
      },
      error: (err) => {
        this.consultando.set(false);
        this.toast.error(err.error?.detail ?? 'No se pudo consultar el clima (¿está corriendo el servicio de clima_externo?).');
      },
    });
  }

  cargarHistorial(): void {
    const nombre = this.form.getRawValue().nombre_granja;
    if (!nombre) return;

    this.cargandoHistorial.set(true);
    this.svc.historial(nombre).subscribe({
      next: (lista) => {
        this.historial.set(lista);
        this.cargandoHistorial.set(false);
      },
      error: () => {
        this.historial.set([]);
        this.cargandoHistorial.set(false);
      },
    });
  }

  claseRiesgo(estado: string | null): string {
    if (!estado) return 'badge-neutral';
    if (estado.includes('ÓPTIMO')) return 'badge-accent';
    if (estado.includes('ALERTA')) return 'badge-amber';
    if (estado.includes('PELIGRO')) return 'badge-danger';
    return 'badge-neutral';
  }
}
