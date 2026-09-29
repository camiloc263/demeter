import { Component, inject, signal } from '@angular/core';
import { JsonPipe } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MlWsService } from '../../core/services/ml-ws.service';
import { ToastService } from '../../shared/toast/toast.service';

@Component({
  selector: 'app-ml-ws',
  standalone: true,
  imports: [ReactiveFormsModule, JsonPipe],
  templateUrl: './ml-ws.component.html',
  styleUrl: './ml-ws.component.scss',
})
export class MlWsComponent {
  private svc = inject(MlWsService);
  private toast = inject(ToastService);
  private fb = inject(FormBuilder);

  enviando = signal(false);
  respuesta = signal<{ status: string; detail: unknown } | null>(null);

  form = this.fb.nonNullable.group({
    numero_telefono: ['', Validators.required],
    corral: ['', Validators.required],
    racion_kg: [5, [Validators.required, Validators.min(0.1)]],
    motivo_ia: ['', Validators.required],
  });

  reenviar(): void {
    if (this.form.invalid || this.enviando()) return;
    this.enviando.set(true);
    this.respuesta.set(null);

    this.svc.reenviar(this.form.getRawValue()).subscribe({
      next: (r) => {
        this.respuesta.set(r);
        this.enviando.set(false);
        this.toast.ok('Reenviado a través de ml_ws.');
      },
      error: (err) => {
        this.enviando.set(false);
        this.toast.error(err.error?.detail ?? 'No se pudo reenviar (¿está corriendo microservicio_notificaciones?).');
      },
    });
  }
}
