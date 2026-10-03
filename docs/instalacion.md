# Manual de instalación y técnico

## Windows / PowerShell
Instalar Python 3.12, Node.js 22 o 24 y Git desde sus sitios oficiales. Obtener el proyecto:
```powershell
git clone https://github.com/GaboGon25/Proyecto_Historia_Leon-.git
Set-Location Proyecto_Historia_Leon-
powershell -ExecutionPolicy Bypass -File scripts/install.ps1
```
El cambio de política se limita a ese proceso para ejecutar el script local inspeccionado. No se altera la política global. El script usa `npm.cmd` para evitar restricciones sobre `npm.ps1`.

Terminal 1, desde la raíz:
```powershell
& backend/.venv/Scripts/python.exe backend/manage.py runserver 127.0.0.1:8000
```
Terminal 2, desde la raíz:
```powershell
Set-Location frontend
npm.cmd run dev -- --port 5173
```
Abrir el puerto 5173 en el navegador de la computadora. Vite envía solicitudes de la API y administración a Django. No se necesita activar el entorno virtual: los comandos invocan su Python directamente.

Crear administrador, desde la raíz:
```powershell
& backend/.venv/Scripts/python.exe backend/manage.py createsuperuser
```
El asistente solicita usuario y contraseña de forma local. No copiar la contraseña a `.env`, documentación ni Git. Acceder a `/admin/` desde la interfaz, iniciar sesión y cerrar sesión al terminar. Cada miembro autorizado debe tener su propia cuenta.

## Variables y configuración
`.env.example` es una referencia: Django lee variables del proceso y **no carga automáticamente un archivo .env**. Establecer en PowerShell:
```powershell
$env:DJANGO_ALLOWED_HOSTS = "localhost,127.0.0.1"
$env:DJANGO_DEBUG = "1"
$env:VITE_API_PROXY = "http://127.0.0.1:8000"
```
En desarrollo se genera una clave temporal si no se define `DJANGO_SECRET_KEY`; puede invalidar sesiones al reiniciar. Para sesiones persistentes definir una clave privada en el proceso o gestor de secretos. En modo no DEBUG la clave es obligatoria. `DJANGO_DB_PATH` permite escoger una SQLite fuera del checkout si se necesita aislar pruebas.

## Feria en red local
Todos los teléfonos y la computadora deben estar en la misma red, que permita comunicación entre dispositivos. Identificar la dirección LAN real de la computadora; no inventarla. Añadirla a `DJANGO_ALLOWED_HOSTS`, reiniciar Django y ejecutar Vite en `0.0.0.0` (el script dev ya lo hace). Abrir solo el puerto 5173 para la red privada de la feria. Mantener Django en loopback, accesible a través del proxy de Vite. Comprobar desde un teléfono la dirección LAN y generar el QR de esa dirección con `/rutas/origenes` si se desea.

Este es un servidor de demostración y edición local. No exponer Vite o `runserver` directamente a Internet. No se entregó URL pública ni se afirmó publicación.

## Comprobaciones
```powershell
& backend/.venv/Scripts/python.exe backend/manage.py check
& backend/.venv/Scripts/python.exe backend/manage.py test history
Set-Location frontend
npm.cmd run build
npx.cmd playwright install chromium
npm.cmd run test:e2e
```
La API debe estar ejecutándose para las pruebas de navegador. PowerShell no se ejecutó en esta máquina Linux: sus instrucciones son una adaptación documentada, pendiente de comprobar en Windows.

## Respaldo y mantenimiento
Detener Django antes de copiar `backend/db.sqlite3`. Guardar respaldo fuera de Git y protegerlo porque incluye usuarios y hashes de contraseña. Para guardar solo contenido de investigación, exportar entidades de `history` con `dumpdata history --indent 2` hacia una ruta privada; revisar antes de publicar cualquier testimonio. Restaurar únicamente datos de confianza. Las migraciones de esquema están versionadas; `seed_history` es repetible y preserva ediciones existentes.

## API
GET `/api/places/`, GET `/api/places/<slug>/`, GET `/api/events/`, GET `/api/routes/`, GET `/api/routes/<slug>/`, GET `/api/questions/`. Lugares acepta `q`, `municipality`, `category` y `period`. POST `/api/quiz/grade/` recibe `{"answers":{"1":0,"2":0}}`; usar los IDs reales entregados por preguntas. No entrega respuestas correctas hasta evaluar. No almacena resultados personales.

## Publicación futura
Preparar HTTPS, clave privada persistente, hosts exactos, `DJANGO_DEBUG=0`, servidor WSGI/ASGI, servicio de archivos estáticos y reglas de proxy para API y administración. Revisar `manage.py check --deploy`. Configurar CSRF y origen conforme al dominio efectivo, respaldos, permisos y licencias. Este despliegue no fue ejecutado ni probado en esta entrega.
