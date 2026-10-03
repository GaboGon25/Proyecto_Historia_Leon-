# Evidencias reales de esta entrega

## Entorno y resultados
Python 3.12.14, Django 5.2.17, Django REST Framework 3.16.1, Node.js 24.19.0, Vite 6.4.3 y Chromium del entorno Linux.

| Comprobación ejecutada | Resultado | Límite |
|---|---|---|
| Instalación inicial y repetición `bash scripts/install.sh` | Correcta: entorno Python, dependencias fijadas, migraciones, semilla repetible, `npm ci` y build | Repetición en la misma máquina; no valida restauración futura |
| `manage.py check` | Sin incidencias | Configuración de desarrollo, no auditoría de despliegue |
| `manage.py makemigrations --check --dry-run` | Sin cambios de esquema pendientes | No reemplaza pruebas de comportamiento |
| `manage.py test history` | 9 pruebas ejecutadas, 9 aprobadas | Base aislada, sin estudiantes ni credenciales de usuarios reales |
| `npm run build` | TypeScript y build Vite correctos | No es un despliegue público |
| Playwright en Chromium | 7 pruebas ejecutadas, 7 aprobadas | API real iniciada; escenarios vacíos/fallidos interceptados |
| Arranque de Django y Vite | Servicios iniciados y consumidos por el navegador | Los procesos deben reiniciarse en futuros entornos |
| Geometría y coordenadas | Dos puntos y límite departamental obtenidos de OSM/Nominatim | Cartografía colaborativa y límite simplificado, sin comprobación de campo |
| Fuentes históricas | Tres documentos de Mapa Nacional de Turismo consultados | UNESCO pendiente de consulta directa y contraste |

## Recorridos de navegador
Inicio → catálogo → buscador → ficha; filtro municipal y ruta por paradas; actividad con 4/4 y 0/4; línea del tiempo sin datos como escenario controlado; mapa con dos puntos reales y apertura de ficha aunque fallen mosaicos, seguido de acontecimiento → ficha; API fallida y reintento; pantalla de 390 px sin desbordamiento y QR generado localmente.

El archivo [playwright-resultados.json](evidencias/playwright-resultados.json) contiene el resultado de la ejecución final con tiempos y nombres de pruebas. Las coordenadas y acontecimientos usados en el recorrido principal son los del catálogo citado, no datos sintéticos. Las pruebas unitarias de validación sí usan datos sintéticos en su base aislada.

## Capturas de la implementación
- [Inicio](evidencias/inicio.png).
- [Mapa y catálogo](evidencias/mapa-catalogo.png): mosaicos externos bloqueados intencionalmente en la captura para evidenciar el límite local, los puntos y la alternativa de lista.
- [Línea del tiempo](evidencias/linea-tiempo.png).
- [Ficha León Viejo](evidencias/ficha-leon-viejo.png).
- [Ruta en móvil](evidencias/ruta-movil.png).

Las capturas muestran el prototipo ejecutado, no bocetos ni fotografías históricas.

## Problemas corregidos durante la verificación
La caché predeterminada de npm no era escribible; se instaló usando `/tmp/leon-npm-cache`. La compilación detectó una colisión entre el componente de mapa y `Map` de JavaScript; se renombró el componente. El primer recorrido del filtro municipal detectó un nombre accesible ambiguo; se corrigió la etiqueta y se repitieron las pruebas. No se desactivó TLS para obtener fuentes o paquetes.

## No ejecutado
Instalación en Windows/PowerShell, evaluación con estudiantes, entrevistas comunitarias, revisión docente, consulta directa del registro UNESCO, publicación en Internet, prueba de un QR desde teléfonos reales y restauración en un entorno nuevo. No hay fotografías históricas incorporadas: se necesita verificar licencia y atribución antes de agregarlas.
