import { Component, computed, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { forkJoin } from 'rxjs';
import { AlimentacionIaService } from '../../core/services/alimentacion-ia.service';
import { InventarioService } from '../../core/services/inventario.service';
import { ToastService } from '../../shared/toast/toast.service';
import { PrediccionDieta, RegistroComida } from '../../core/models/nutricion.model';
import { Cerdo } from '../../core/models/cerdo.model';

@Component({
  selector: 'app-alimentacion-ia',
  standalone: true,
  imports: [ReactiveFormsModule, DatePipe],
  templateUrl: './alimentacion-ia.component.html',
  styleUrl: './alimentacion-ia.component.scss',
})
export class AlimentacionIaComponent {
  private svc = inject(AlimentacionIaService);
  private inventarioSvc = inject(InventarioService);
  private toast = inject(ToastService);
  private fb = inject(FormBuilder);

  // --- Predicción de dieta ---
  calculando = signal(false);
  prediccion = signal<PrediccionDieta | null>(null);

  formDieta = this.fb.nonNullable.group({
    edad_dias: [60, [Validators.required, Validators.min(1), Validators.max(400)]],
    peso_actual_kg: [25, [Validators.required, Validators.min(0.1)]],
    temperatura_c: [24, Validators.required],
  });

  predecir(): void {
    if (this.formDieta.invalid || this.calculando()) return;
    this.calculando.set(true);
    this.prediccion.set(null);

    this.svc.predecirDieta(this.formDieta.getRawValue()).subscribe({
      next: (resultado) => {
        this.prediccion.set(resultado);
        this.calculando.set(false);
      },
      error: (err) => {
        this.calculando.set(false);
        this.toast.error(err.error?.detail ?? 'El modelo de nutrición no está disponible en este momento.');
      },
    });
  }

  get hayAdvertencia(): boolean {
    return (this.prediccion()?.analisis ?? '').includes('⚠️');
  }

  // --- Historial por RFID ---
  buscando = signal(false);
  buscado = signal(false);
  historial = signal<RegistroComida[]>([]);
  cerdo = signal<Cerdo | null | undefined>(undefined);

  formHistorial = this.fb.nonNullable.group({
    rfid: ['', Validators.required],
  });

  readonly resumen = computed(() => {
    const lista = this.historial();
    if (lista.length === 0) return null;
    const totalKg = lista.reduce((acc, r) => acc + r.racion_servida_kg, 0);
    return {
      eventos: lista.length,
      totalKg: Math.round(totalKg * 100) / 100,
      promedioKg: Math.round((totalKg / lista.length) * 100) / 100,
      // el backend ya ordena de más reciente a más antiguo
      ultima: lista[0].fecha_hora,
    };
  });

  buscarHistorial(): void {
    if (this.formHistorial.invalid || this.buscando()) return;
    const rfid = this.formHistorial.getRawValue().rfid;
    this.buscando.set(true);
    this.buscado.set(false);
    this.cerdo.set(undefined);

    forkJoin({
      historial: this.svc.historialCerdo(rfid),
      cerdo: this.inventarioSvc.buscarPorEtiqueta(rfid),
    }).subscribe({
      next: ({ historial, cerdo }) => {
        this.historial.set(historial);
        this.cerdo.set(cerdo ?? null);
        this.buscando.set(false);
        this.buscado.set(true);
      },
      error: () => {
        this.historial.set([]);
        this.cerdo.set(null);
        this.buscando.set(false);
        this.buscado.set(true);
        this.toast.error('No se pudo consultar el historial.');
      },
    });
  }
}
