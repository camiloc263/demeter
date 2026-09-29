import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { NotificacionesService } from '../../core/services/notificaciones.service';
import { ToastService } from '../../shared/toast/toast.service';
import { ResultadoNotificacion } from '../../core/models/notificacion.model';

@Component({
  selector: 'app-notificaciones',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './notificaciones.component.html',
  styleUrl: './notificaciones.component.scss',
})
export class NotificacionesComponent {
  private svc = inject(NotificacionesService);
  private toast = inject(ToastService);
  private fb = inject(FormBuilder);

  // --- Evaluar si es buen momento para notificar ---
  evaluando = signal(false);
  resultadoEvaluacion = signal<ResultadoNotificacion | null>(null);

  formEvaluar = this.fb.nonNullable.group({
    nombre_corral: ['', Validators.required],
    telefono_trabajador: ['', Validators.required],
    hora_del_dia: [10, [Validators.required, Validators.min(0), Validators.max(24)]],
    temperatura_actual_c: [24, Validators.required],
    horas_desde_ultima_comida: [9, [Validators.required, Validators.min(0)]],
    raciones_pendientes_kg: [5, [Validators.required, Validators.min(0.1)]],
  });

  evaluar(): void {
    if (this.formEvaluar.invalid || this.evaluando()) return;
    this.evaluando.set(true);
    this.resultadoEvaluacion.set(null);

    this.svc.evaluar(this.formEvaluar.getRawValue()).subscribe({
      next: (resultado) => {
        this.resultadoEvaluacion.set(resultado);
        this.evaluando.set(false);
      },
      error: (err) => {
        this.evaluando.set(false);
        this.toast.error(err.error?.detail ?? 'No se pudo evaluar la notificación.');
      },
    });
  }

  // --- Enviar alerta directa (sin pasar por el modelo) ---
  enviando = signal(false);
  resultadoDirecto = signal<ResultadoNotificacion | null>(null);

  formDirecto = this.fb.nonNullable.group({
    numero_telefono: ['', Validators.required],
    corral: ['', Validators.required],
    racion_kg: [5, [Validators.required, Validators.min(0.1)]],
    motivo_ia: ['', Validators.required],
  });

  enviarDirecto(): void {
    if (this.formDirecto.invalid || this.enviando()) return;
    this.enviando.set(true);
    this.resultadoDirecto.set(null);

    this.svc.notificarDirecto(this.formDirecto.getRawValue()).subscribe({
      next: (resultado) => {
        this.resultadoDirecto.set(resultado);
        this.enviando.set(false);
        this.toast.ok('Alerta enviada.');
      },
      error: (err) => {
        this.enviando.set(false);
        this.toast.error(err.error?.detail ?? 'No se pudo enviar la alerta.');
      },
    });
  }
}
