# Guía de ejecución — Demeter

Paso a paso para levantar los 12 microservicios en una máquina Windows nueva, probar el flujo real de la granja, y apagar todo al terminar. Para entender *por qué* cada cosa funciona así (arquitectura, patrones, endpoints de cada servicio), ver [ARQUITECTURA.md](ARQUITECTURA.md) — esta guía es solo la parte operativa.

## 0. Requisitos previos

- **Python 3.13** instalado y en el PATH.
- Haber clonado el repo en, por ejemplo, `D:\proyectos\Demeter`.
- (Opcional) `git` para el control de versiones.

## 1. Preparar el entorno (una sola vez)

Desde la raíz del repo (`D:\proyectos\Demeter`):

```powershell
# 1. Crear el entorno virtual
python -m venv venv

# 2. Activarlo (PowerShell)
.\venv\Scripts\Activate.ps1
# — si usas Git Bash / WSL en su lugar:
# source venv/Scripts/activate

# 3. Instalar dependencias
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 4. Instalar la librería compartida en modo editable
#    (sin esto, ningún servicio puede hacer "import demeter_core")
pip install -e core_compartido
```

Verifica que quedó instalada:

```powershell
pip show demeter_core
```

Debe mostrar `Editable project location: ...\core_compartido`.

> **Windows + emojis**: varios servicios imprimen mensajes con emoji al arrancar (✅, ⚠️, ❌). Si el proceso se cae con `UnicodeEncodeError` al iniciar, es porque la consola de Windows no está en UTF-8. Corrígelo una vez por sesión de terminal:
> ```powershell
> $env:PYTHONIOENCODING = "utf-8"
> ```
> (en Git Bash: `export PYTHONIOENCODING=utf-8`).

## 2. Levantar los servicios

**Todos se ejecutan desde la raíz del repositorio** (no entres a la carpeta de cada servicio), excepto `notificaciones` y `ml_ws`, que todavía usan el patrón antiguo de imports (ver `ARQUITECTURA.md`, sección 5). Cada uno necesita **su propia terminal** (o lánzalos en segundo plano).

Abre una terminal por servicio y activa el venv en cada una (`.\venv\Scripts\Activate.ps1`), luego:

```powershell
# 8000 — raciones por corral
python -m uvicorn microservicio_alimentacion.main:app --port 8000

# 8001 — gestión de corrales
python -m uvicorn microservicio_corrales.main:app --port 8001

# 8002 — comedero RFID + IA nutricional
python -m uvicorn microservicio_alimentacion_ia.main:app --port 8002

# 8003 — inventario de cerdos
python -m uvicorn microservicio_inventario.main:app --port 8003

# 8004 — sensores IoT
python -m uvicorn microservicio_iot.main:app --port 8004

# 8005 — usuarios / JWT
python -m uvicorn microservicio_usuarios.main:app --port 8005

# 8006 — predicción de estrés calórico
python -m uvicorn microservicio_ia.main:app --port 8006

# 8007 — motor de decisión de alertas
python -m uvicorn microservicio_ia_notificaciones.main:app --port 8007

# 8008 — clima satelital + diagnóstico
python -m uvicorn microservicio_clima_externo.main:app --port 8008

# 8009 — órdenes de trabajo (SOP)
python -m uvicorn microservicio_ordenes_trabajo.main:app --port 8009
```

Estos dos van desde **su propia carpeta** (import antiguo, ver deuda técnica en `ARQUITECTURA.md`):

```powershell
# 8010 — despacho de notificaciones WhatsApp
cd microservicio_notificaciones
python -m uvicorn main:app --port 8010
cd ..

# 8011 — reenvío (infra, opcional — no imprescindible para el flujo de negocio)
cd microservicio_ml_ws
python -m uvicorn main:app --port 8011
cd ..
```

No necesitas los 12 arriba para probar algo puntual — levanta solo los que te interesan y sus dependencias directas (ver el diagrama de comunicación en `ARQUITECTURA.md`, sección 4).

### Atajo: lanzar todo con un solo script

Si prefieres no abrir 12 terminales, este script de PowerShell abre una ventana por servicio:

```powershell
$servicios = @(
    @{ Nombre = "alimentacion";      Puerto = 8000; Dir = "." },
    @{ Nombre = "corrales";          Puerto = 8001; Dir = "." },
    @{ Nombre = "alimentacion_ia";   Puerto = 8002; Dir = "." },
    @{ Nombre = "inventario";        Puerto = 8003; Dir = "." },
    @{ Nombre = "iot";               Puerto = 8004; Dir = "." },
    @{ Nombre = "usuarios";          Puerto = 8005; Dir = "." },
    @{ Nombre = "ia";                Puerto = 8006; Dir = "." },
    @{ Nombre = "ia_notificaciones"; Puerto = 8007; Dir = "." },
    @{ Nombre = "clima_externo";     Puerto = 8008; Dir = "." },
    @{ Nombre = "ordenes_trabajo";   Puerto = 8009; Dir = "." },
    @{ Nombre = "notificaciones";    Puerto = 8010; Dir = "microservicio_notificaciones" },
    @{ Nombre = "ml_ws";             Puerto = 8011; Dir = "microservicio_ml_ws" }
)

foreach ($s in $servicios) {
    $modulo = if ($s.Dir -eq ".") { "microservicio_$($s.Nombre).main:app" } else { "main:app" }
    $cmd = "cd '$PWD\$($s.Dir)'; .\venv\Scripts\Activate.ps1; " +
           "`$env:PYTHONIOENCODING='utf-8'; " +
           "python -m uvicorn $modulo --port $($s.Puerto)"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $cmd
}
```

Guárdalo como `iniciar_todo.ps1` en la raíz y ejecútalo con `.\iniciar_todo.ps1`. Ábrelo con cuidado la primera vez para confirmar que cada ventana arranca bien.

## 3. Levantar el frontend (Angular)

El frontend vive en `frontend/` — una app Angular que consume `usuarios`, `corrales`, `inventario`, `alimentacion`, `iot` y `ordenes_trabajo` (los seis servicios "de dominio" con pantalla propia; ver `frontend/src/app/core/config/api.config.ts` para las URLs).

```powershell
cd frontend
npm install          # solo la primera vez
npm start             # sirve en http://localhost:4200
```

Necesitas al menos `usuarios`, `corrales`, `inventario`, `alimentacion`, `iot` y `ordenes_trabajo` corriendo (sección 2) para que el frontend funcione de verdad — si falta alguno, esa pantalla en particular mostrará un error de carga, pero el resto de la app sigue usable.

**Primer ingreso**: no hay pantalla de registro en el frontend (a propósito — ver ARQUITECTURA.md sección 5). Crea el primer usuario administrador por API antes de intentar loguearte:

```bash
curl -X POST http://127.0.0.1:8005/usuarios/ -H "Content-Type: application/json" \
  -d '{"username":"admin","rol":"administrador","password":"cambia-esto-123"}'
```

Luego entra en `http://localhost:4200` con ese usuario y contraseña.

> **Nota sobre `npx ng serve` vs `npm start`**: si usas `npx ng serve` directamente en vez de `npm start`, la primera vez puede quedarse "colgado" sin mostrar nada — es el prompt de analítica de Angular CLI esperando una respuesta que nunca llega en una terminal no interactiva. Usa `npm start` (que ya invoca el `ng` local del proyecto) o define `NG_CLI_ANALYTICS=false` antes de correrlo.

## 4. Verificar que todo está arriba

Con los servicios corriendo, en cualquier terminal (nueva, sin activar el venv):

```bash
for p in 8000 8001 8002 8003 8004 8005 8006 8008 8009 8010; do
  echo "puerto $p:"; curl -s "http://127.0.0.1:$p/"; echo
done
```

Cada uno debe responder `{"status":"OK","service":"..."}`. `8007` (ia_notificaciones) y `8011` (ml_ws) no tienen ruta `/` — confírmalos con `curl http://127.0.0.1:8007/docs` (debe dar 200).

Cada servicio también expone documentación interactiva en `http://127.0.0.1:<puerto>/docs` (Swagger UI de FastAPI) — útil para probar endpoints a mano sin escribir `curl`.

## 5. Probar el flujo real de la granja

Este recorrido usa `curl`; en PowerShell reemplaza `curl` por `curl.exe` (PowerShell alias `curl` a `Invoke-WebRequest`, que tiene otra sintaxis).

**5.1 — Crear el primer usuario administrador** (el registro es público a propósito, para poder arrancar el sistema desde cero):

```bash
curl -X POST http://127.0.0.1:8005/usuarios/ -H "Content-Type: application/json" \
  -d '{"username":"admin","rol":"administrador","password":"cambia-esto-123"}'
```

**5.2 — Iniciar sesión y guardar el token:**

```bash
TOKEN=$(curl -s -X POST http://127.0.0.1:8005/usuarios/login -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"cambia-esto-123"}' | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
echo $TOKEN
```

**5.3 — Crear un corral** (requiere el token: crear corrales es una acción humana protegida):

```bash
curl -X POST http://127.0.0.1:8001/corrales/ -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"nombre":"Corral 1","capacidad_maxima":20,"ancho_m":6,"largo_m":8,"etapa":"Engorde"}'
```

**5.4 — Registrar un cerdo en ese corral** (valida automáticamente contra `corrales` que la etapa coincida y no haya hacinamiento):

```bash
curl -X POST http://127.0.0.1:8003/cerdos/ -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"etiqueta":"C-001","fecha_nacimiento":"2025-01-01","etapa":"Engorde","peso_kg":45,"corral":"Corral 1"}'
```

**5.5 — Registrar que se alimentó el corral** (valida contra `inventario` que el corral tenga cerdos):

```bash
curl -X POST http://127.0.0.1:8000/alimentacion/ -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"corral":"Corral 1","tipo_alimento":"Concentrado","cantidad_kg":5.5}'
```

**5.6 — Simular una lectura de sensor** (sin token: es telemetría de dispositivo, no acción humana):

```bash
curl -X POST http://127.0.0.1:8004/iot/ -H "Content-Type: application/json" \
  -d '{"corral":"Corral 1","temperatura_c":26.5,"humedad_pct":58}'
```

O deja corriendo el sensor simulado de verdad (edita `CORRAL_OBJETIVO` en el archivo para que apunte a un corral que exista):

```bash
python sensor_virtual.py
```

Si algún paso devuelve `401 Unauthorized`, el token expiró (dura 1h) o no se copió bien — repite el paso 5.2. Si devuelve `404`/`400` con un mensaje sobre el corral o el cerdo, es una regla de negocio real rechazando la operación (ver la sección 03 de `ARQUITECTURA.md` para el porqué de cada validación), no un error de conexión.

## 6. Correr los tests

Sin necesidad de tener ningún servicio corriendo (los tests son herméticos: base de datos en memoria y llamadas a otros servicios mockeadas):

```bash
python -m pytest
```

Debe terminar en verde. Si algo falla, es una regresión real — no lo ignores.

## 7. Apagar todo

Cierra cada ventana de terminal (`Ctrl+C` primero para que uvicorn cierre limpio, luego cierra la ventana), o si usaste `iniciar_todo.ps1`, cierra las 12 ventanas que abrió.

Las bases de datos SQLite (`*.db`) quedan en la carpeta de cada servicio entre una corrida y otra — si quieres empezar de cero, bórralas (están en `.gitignore`, no se suben al repo).

## 8. Problemas comunes

| Síntoma | Causa | Solución |
|---|---|---|
| `UnicodeEncodeError` al arrancar `ia` o `ia_notificaciones` | Consola de Windows no está en UTF-8 | `$env:PYTHONIOENCODING = "utf-8"` antes de arrancar (ver sección 1) |
| `ModuleNotFoundError: No module named 'demeter_core'` | No se instaló la librería compartida | `pip install -e core_compartido` desde la raíz |
| `ModuleNotFoundError: No module named 'services'` (o `'core'`, `'db'`) | Se intentó correr un servicio con `cd` a su carpeta cuando debía ser desde la raíz (o viceversa) | Revisa la sección 2: solo `notificaciones` y `ml_ws` se corren desde su propia carpeta |
| `OperationalError: no such column` | Un `.db` viejo quedó con un esquema desactualizado (`create_all` no migra columnas nuevas) | Borra ese archivo `.db` puntual y vuelve a arrancar el servicio — se recrea con el esquema actual |
| `401 Unauthorized` en un POST/PATCH/DELETE | Falta el header `Authorization: Bearer <token>`, o el token expiró (1h) | Repite el login (paso 5.2) |
| `403 Forbidden` en `GET /usuarios/` | El usuario logueado no tiene `rol: "administrador"` | Usa el usuario admin creado en el paso 5.1, o cambia el rol de otro usuario directamente en la base |
| Un servicio no puede validar contra otro (`503 ... está fuera de línea`) | El servicio del que depende no está corriendo | Revisa el diagrama de dependencias en `ARQUITECTURA.md` sección 4 y levanta ese servicio también |
| Puerto ya en uso | Quedó un proceso anterior corriendo | Windows: `netstat -ano \| findstr :8000` para hallar el PID, luego `taskkill /PID <pid> /F` |
