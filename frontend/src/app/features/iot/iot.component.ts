import { Component, OnInit, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { IotService } from '../../core/services/iot.service';
import { CorralesService } from '../../core/services/corrales.service';
import { Corral } from '../../core/models/corral.model';
import { LecturaIot } from '../../core/models/lectura.model';

@Component({
  selector: 'app-iot',
  standalone: true,
  imports: [FormsModule, DatePipe],
  templateUrl: './iot.component.html',
  styleUrl: './iot.component.scss',
})
export class IotComponent implements OnInit {
  private svc = inject(IotService);
  private corralesSvc = inject(CorralesService);

  corrales = signal<Corral[]>([]);
  corralSeleccionado = signal('');
  lecturas = signal<LecturaIot[]>([]);
  cargando = signal(false);
  sinLecturas = signal(false);

  ngOnInit(): void {
    this.corralesSvc.listar().subscribe((lista) => {
      this.corrales.set(lista);
      if (lista.length) this.seleccionar(lista[0].nombre);
    });
  }

  seleccionar(nombre: string): void {
    this.corralSeleccionado.set(nombre);
    this.sinLecturas.set(false);
    this.cargando.set(true);
    this.svc.lecturasPorCorral(nombre, 20).subscribe({
      next: (lista) => {
        this.lecturas.set(lista);
        this.cargando.set(false);
      },
      error: () => {
        this.lecturas.set([]);
        this.sinLecturas.set(true);
        this.cargando.set(false);
      },
    });
  }

  get ultima(): LecturaIot | undefined {
    return this.lecturas()[0];
  }
}
