# Manual de usuario

## Estudiantes y docentes
1. En inicio elegir **Iniciar recorrido**.
2. En **Explorar** escribir el nombre de un lugar o seleccionar municipio y tema. El filtro de período aparece cuando exista contenido con período registrado.
3. Abrir la ficha desde una tarjeta o un marcador disponible. Leer descripción, estado, afirmaciones y fuentes. Una referencia pendiente no demuestra una afirmación.
4. En **Línea del tiempo** filtrar por lugar y abrir el enlace a su ficha. Solo se muestran acontecimientos con fuente y revisión verificadas. Actualmente hay cuatro acontecimientos respaldados por Mapa Nacional de Turismo; la consulta directa de UNESCO sigue pendiente.
5. En **Rutas** seleccionar un recorrido; abrir cada ficha y avanzar por las paradas. No interpretar las paradas como trayecto físico.
6. En **Actividad** responder todas las preguntas y finalizar. Revisar las explicaciones; se puede repetir sin guardar información personal.
7. En **Feria** introducir la dirección real accesible desde teléfonos y descargar el QR. Probarlo antes de imprimir.

## Si no hay Internet
El catálogo y los contenidos guardados se consultan con ambos servidores locales iniciados. Si no cargan mosaicos, usar la lista. Los enlaces de fuentes y futuros recursos remotos pueden requerir Internet. Si la API falla, iniciar Django y pulsar **Reintentar**.

## Administrador / investigador
Crear usuario con `createsuperuser` y entrar por **Administrar contenidos**. Registrar primero fuente con institución, URL, fecha real de consulta y notas. Marcarla verificada solo después de leerla. Agregar o editar lugar y afirmaciones, citando por separado cada hecho y relato. Las coordenadas requieren fuente verificada. Para marcar una ficha revisada, guardar primero una afirmación respaldada; regresar al formulario y cambiar el estado después de revisar el contenido completo.

Agregar acontecimientos con año comprobado y fuente. El año no sirve para fechas exactas ni intervalos: ampliar el modelo si la investigación lo requiere, sin inventar precisión. Agregar rutas y ordenar sus paradas mediante números únicos. Registrar recursos con autor, licencia y permiso; aprobar únicamente los que estén autorizados. Las otras seis ubicaciones no se dibujan hasta verificar sus coordenadas. Agregar preguntas, opciones como lista JSON, índice correcto desde cero, explicación y fuente cuando evalúen historia.

Cerrar sesión al terminar. No compartir contraseñas ni aprobar contenido solo para hacer que aparezca en el mapa o la línea del tiempo.
