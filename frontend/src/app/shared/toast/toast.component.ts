import { Component, inject } from '@angular/core';
import { ToastService } from './toast.service';

@Component({
  selector: 'app-toast',
  standalone: true,
  template: `
    <div class="toast-stack">
      @for (t of toast.toasts(); track t.id) {
        <div class="toast" [class.toast-error]="t.tipo === 'error'">
          <span class="toast-icon">{{ t.tipo === 'ok' ? '✓' : '!' }}</span>
          <span>{{ t.mensaje }}</span>
          <button type="button" class="toast-close" (click)="toast.cerrar(t.id)" aria-label="Cerrar">×</button>
        </div>
      }
    </div>
  `,
  styles: [`
    .toast-stack {
      position: fixed;
      top: 1rem;
      right: 1rem;
      z-index: 1000;
      display: flex;
      flex-direction: column;
      gap: .6rem;
      max-width: 360px;
    }
    .toast {
      display: flex;
      align-items: center;
      gap: .6rem;
      background: var(--surface);
      border: 1px solid var(--line);
      border-left: 3px solid var(--accent);
      border-radius: 8px;
      padding: .7rem .8rem;
      box-shadow: var(--shadow-md);
      font-size: .86rem;
      color: var(--ink);
      animation: slide-in .18s ease;
    }
    .toast-error { border-left-color: var(--danger); }
    .toast-icon {
      flex: none;
      width: 1.3rem; height: 1.3rem;
      border-radius: 50%;
      display: flex; align-items: center; justify-content: center;
      font-size: .72rem; font-weight: 700;
      background: var(--accent-soft); color: var(--accent);
    }
    .toast-error .toast-icon { background: var(--danger-soft); color: var(--danger); }
    .toast-close {
      margin-left: auto;
      background: none; border: none; cursor: pointer;
      font-size: 1.1rem; color: var(--ink-faint); line-height: 1;
      padding: 0 .2rem;
    }
    @keyframes slide-in {
      from { opacity: 0; transform: translateY(-6px); }
      to { opacity: 1; transform: translateY(0); }
    }
  `],
})
export class ToastComponent {
  toast = inject(ToastService);
}
