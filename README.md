# León en el tiempo
Prototipo educativo universitario sobre el departamento de León, Nicaragua, para Historia e Identidad Nacional de la UNI.

**Estado:** primera entrega tecnológica. Catálogo de ocho fichas citadas: León Viejo y Catedral con revisión documental inicial; las otras seis pendientes de ampliación. Mapa con dos ubicaciones OSM, límite departamental local, cuatro acontecimientos citados y cuatro preguntas. API, administración y rutas funcionales. UNESCO permanece pendiente de consulta directa; se usó Mapa Nacional de Turismo para el contenido inicial. Consulta `docs/fuentes.md`.

## Inicio rápido en la nube / Linux
Requisitos: Python 3.12 y Node.js 22 o 24.
```bash
bash scripts/install.sh
# Terminal 1
backend/.venv/bin/python backend/manage.py runserver 127.0.0.1:8000
# Terminal 2
cd frontend
npm run dev -- --port 5173
```
La interfaz usa el puerto 5173 y la API el 8000. Para administración crea tu propia cuenta, sin guardar su contraseña en Git:
```bash
backend/.venv/bin/python backend/manage.py createsuperuser
```
No hay credenciales predeterminadas. `/admin/` utiliza sesión, permisos de Django y CSRF. La API pública es de lectura, excepto la calificación de preguntas, que no modifica contenidos.

## Pruebas
Con la API iniciada:
```bash
backend/.venv/bin/python backend/manage.py test history
cd frontend
npm run build
# En este entorno Chromium está instalado en /usr/bin/chromium
PLAYWRIGHT_CHROMIUM_EXECUTABLE=/usr/bin/chromium npm run test:e2e
```
En otras máquinas instala el navegador de pruebas con `npx playwright install chromium` y ejecuta `npm run test:e2e`. La configuración inicia Vite; la API debe estar iniciada previamente. Las pruebas del mapa y de la línea del tiempo usan las ubicaciones y acontecimientos reales del catálogo citado. Los escenarios de API vacía o fallida se interceptan únicamente en el navegador. Las pruebas de validación del backend usan una base aislada con datos sintéticos.

## Documentación
- [Propuesta e investigación en curso](docs/propuesta.md)
- [Diagramas](docs/diagramas.md)
- [Fuentes y créditos](docs/fuentes.md)
- [Instalación en Windows y manual técnico](docs/instalacion.md)
- [Manual de usuario](docs/manual-usuario.md)
- [Prueba con estudiantes](docs/evaluacion-usuarios.md)
- [Demostración y video de dos minutos](docs/feria.md)
- [Evidencias de pruebas](docs/evidencias.md)

## Estructura
`frontend/`: React, Vite, TypeScript, Leaflet y generación de QR.
`backend/`: Django REST Framework, administración, modelo y migraciones.
`docs/`: documentación académica y técnica.
`scripts/`: instalación reproducible.

## Sin conexión
Una vez instaladas las dependencias y arrancados ambos servidores, catálogo, fichas, rutas, preguntas y administración funcionan localmente. Los mosaicos OpenStreetMap, las fuentes institucionales y futuros recursos remotos necesitan Internet. La lista permite consultar fichas aunque falle el mapa. El límite departamental OSM se guarda localmente y se muestra aunque fallen los mosaicos. No se implementó un sitio alojado sin servidor ni un modo PWA.

## Alcance de publicación
Los servidores de desarrollo no deben usarse como despliegue público. Revisa `docs/instalacion.md` para HTTPS, clave, hosts y servicio estático. El QR requiere una dirección accesible desde los teléfonos; generarlo no publica el sitio.
