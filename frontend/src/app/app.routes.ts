import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';
import { ShellComponent } from './layout/shell/shell.component';
import { LoginComponent } from './features/login/login.component';
import { DashboardComponent } from './features/dashboard/dashboard.component';
import { CorralesComponent } from './features/corrales/corrales.component';
import { InventarioComponent } from './features/inventario/inventario.component';
import { AlimentacionComponent } from './features/alimentacion/alimentacion.component';
import { IotComponent } from './features/iot/iot.component';
import { OrdenesComponent } from './features/ordenes/ordenes.component';
import { AlimentacionIaComponent } from './features/alimentacion-ia/alimentacion-ia.component';
import { ClimaComponent } from './features/clima/clima.component';
import { NotificacionesComponent } from './features/notificaciones/notificaciones.component';
import { IaNotificacionesComponent } from './features/ia-notificaciones/ia-notificaciones.component';
import { MlWsComponent } from './features/ml-ws/ml-ws.component';

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  {
    path: '',
    component: ShellComponent,
    canActivate: [authGuard],
    children: [
      { path: '', pathMatch: 'full', redirectTo: 'dashboard' },
      { path: 'dashboard', component: DashboardComponent },
      { path: 'corrales', component: CorralesComponent },
      { path: 'inventario', component: InventarioComponent },
      { path: 'alimentacion', component: AlimentacionComponent },
      { path: 'iot', component: IotComponent },
      { path: 'ordenes', component: OrdenesComponent },
      { path: 'alimentacion-ia', component: AlimentacionIaComponent },
      { path: 'clima', component: ClimaComponent },
      { path: 'notificaciones', component: NotificacionesComponent },
      { path: 'ia-notificaciones', component: IaNotificacionesComponent },
      { path: 'ml-ws', component: MlWsComponent },
    ],
  },
  { path: '**', redirectTo: 'dashboard' },
];
