// URLs de los microservicios (ver ARQUITECTURA.md, sección 2 — mapa de servicios).
// En desarrollo cada uno corre en localhost con su puerto fijo.
export const API = {
  usuarios: 'http://127.0.0.1:8005',
  corrales: 'http://127.0.0.1:8001',
  inventario: 'http://127.0.0.1:8003',
  alimentacion: 'http://127.0.0.1:8000',
  iot: 'http://127.0.0.1:8004',
  ordenes: 'http://127.0.0.1:8009',
  alimentacionIa: 'http://127.0.0.1:8002',
  clima: 'http://127.0.0.1:8008',
  notificaciones: 'http://127.0.0.1:8010',
  iaNotificaciones: 'http://127.0.0.1:8007',
  mlWs: 'http://127.0.0.1:8011',
} as const;
