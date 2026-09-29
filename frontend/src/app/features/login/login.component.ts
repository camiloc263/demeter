import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss',
})
export class LoginComponent {
  private fb = inject(FormBuilder);
  private auth = inject(AuthService);
  private router = inject(Router);

  cargando = signal(false);
  error = signal<string | null>(null);

  form = this.fb.nonNullable.group({
    username: ['', Validators.required],
    password: ['', Validators.required],
  });

  enviar(): void {
    if (this.form.invalid || this.cargando()) return;

    this.cargando.set(true);
    this.error.set(null);

    this.auth.login(this.form.getRawValue()).subscribe({
      next: () => {
        this.cargando.set(false);
        this.router.navigate(['/dashboard']);
      },
      error: (err) => {
        this.cargando.set(false);
        this.error.set(
          err.status === 401
            ? 'Usuario o contraseña incorrectos.'
            : 'No se pudo conectar con el servicio de usuarios (¿está corriendo en el puerto 8005?).',
        );
      },
    });
  }
}
