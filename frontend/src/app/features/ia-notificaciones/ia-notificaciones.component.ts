import { Component, inject, signal } from '@angular/core';
import { JsonPipe, NgClass } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { IaNotificacionesService } from '../../core/services/ia-notificaciones.service';
import { ToastService } from '../../shared/toast/toast.service';
import { DecisionAlerta } from '../../core/models/decision-alerta.model';

@Component({
  selector: 'app-ia-notificaciones',
  standalone: true,
  imports: [ReactiveFormsModule, NgClass, JsonPipe],
  templateUrl: './ia-notificaciones.component.html',
  styleUrl: './ia-notificaciones.component.scss',
})
export class IaNotificacionesComponent {
  private svc = inject(IaNotificacionesService);
  private toast = inject(ToastService);
  private fb = inject(FormBuilder);

  evaluando = signal(false);
  decision = signal<DecisionAlerta | null>(null);

  form = this.fb.nonNullable.group({
    corral: ['', Validators.required],
    numero_telefono: ['', Validators.required],
    temperatura_c: [24, Validators.required],
    humedad_pct: [60, [Validators.required, Validators.min(0), Validators.max(100)]],
    peso_promedio_kg: [100, [Validators.required, Validators.min(1)]],
  });

  evaluar(): void {
    if (this.form.invalid || this.evaluando()) return;
    this.evaluando.set(true);
    this.decision.set(null);

    const v = this.form.getRawValue();
    this.svc
      .evaluarYNotificar({
        corral: v.corral,
        numero_telefono: v.numero_telefono,
        datos_clima: {
          temperatura_c: v.temperatura_c,
          humedad_pct: v.humedad_pct,
          peso_promedio_kg: v.peso_promedio_kg,
        },
      })
      .subscribe({
        next: (resultado) => {
          this.decision.set(resultado);
          this.evaluando.set(false);
          if (resultado.accion === 'NOTIFICAR_WHATSAPP_URGENTE') {
            this.toast.ok('La IA decidió notificar por WhatsApp — despacho automático realizado.');
          }
        },
        error: (err) => {
          this.evaluando.set(false);
          this.toast.error(err.error?.detail ?? 'No se pudo evaluar la decisión.');
        },
      });
  }

  claseAccion(accion: string): string {
    if (accion === 'NOTIFICAR_WHATSAPP_URGENTE') return 'badge-danger';
    if (accion === 'NOTIFICAR_EMAIL') return 'badge-amber';
    if (accion === 'OMITIR_NOTIFICACION') return 'badge-neutral';
    return 'badge-neutral';
  }

  etiquetaAccion(accion: string): string {
    const mapa: Record<string, string> = {
      NOTIFICAR_WHATSAPP_URGENTE: 'WhatsApp urgente',
      NOTIFICAR_EMAIL: 'Notificar por email',
      OMITIR_NOTIFICACION: 'Omitir notificación',
    };
    return mapa[accion] ?? accion;
  }
}
