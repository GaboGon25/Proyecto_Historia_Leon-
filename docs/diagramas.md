# Diagramas del sistema

## Arquitectura
```mermaid
flowchart LR
 U[Estudiante o docente] --> R[React + Vite + TypeScript]
 R -->|API JSON /api| D[Django REST Framework]
 A[Administrador autenticado] -->|Sesión y CSRF /admin| D
 D --> S[(SQLite)]
 R -. mosaicos opcionales .-> O[OpenStreetMap]
 R --> Q[QR generado en el navegador]
```
En desarrollo Vite envía `/api`, `/admin` y `/static` al puerto 8000. El navegador no necesita CORS porque opera sobre el mismo origen de Vite.

## Entidad relación
```mermaid
erDiagram
 MUNICIPIO ||--o{ LUGAR : contiene
 LUGAR }o--o{ FUENTE : consulta
 LUGAR ||--o{ AFIRMACION : explica
 FUENTE ||--o{ AFIRMACION : respalda
 FUENTE ||--o{ LUGAR : verifica_coordenadas
 LUGAR ||--o{ ACONTECIMIENTO : relaciona
 FUENTE ||--o{ ACONTECIMIENTO : fecha
 LUGAR ||--o{ RECURSO_MULTIMEDIA : presenta
 RUTA_TEMATICA ||--o{ PARADA_DE_RUTA : ordena
 LUGAR ||--o{ PARADA_DE_RUTA : aparece
 LUGAR ||--o{ PREGUNTA : contextualiza
 FUENTE |o--o{ PREGUNTA : fundamenta
 LUGAR {
  int id PK
  string slug UK
  int municipio_id FK
  text description
  string review_status
  float latitude
  float longitude
  int coordinate_source_id FK
 }
 FUENTE {
  int id PK
  string institution
  string url
  string publication_date
  date accessed_on
  boolean verified
 }
 AFIRMACION {
  int id PK
  int lugar_id FK
  int fuente_id FK
  text text
  string locator
  string kind
 }
 ACONTECIMIENTO {
  int id PK
  int lugar_id FK
  int fuente_id FK
  int year
  boolean verified
 }
 PARADA_DE_RUTA {
  int id PK
  int ruta_id FK
  int lugar_id FK
  int order
  text prompt
 }
 PREGUNTA {
  int id PK
  int lugar_id FK
  int fuente_id FK
  json options
  int correct_index
  text explanation
 }
```
La entidad Afirmación añade trazabilidad por hecho o relato. Lugar–Fuente se implementa con una tabla intermedia de Django. El par ruta/orden es único. Las coordenadas aceptan nulos; no se dibujan marcadores sin respaldo.

## Navegación y pantallas
```mermaid
flowchart TD
 I[Inicio] --> E[Explorar: búsqueda, filtros, mapa y lista]
 E --> F[Ficha: contexto, importancia, citas y recursos]
 I --> T[Línea del tiempo]
 T --> F
 I --> R[Rutas]
 R --> P[Parada anterior o siguiente]
 P --> F
 P --> Q[Actividad y resultado explicado]
 I --> QR[Feria y generación de QR]
 I --> L[Inicio de sesión administrativo]
 L --> A[Edición de contenidos]
```
Inicio: portada de propósito y acceso al recorrido. Explorar: filtros superiores, mapa y tarjetas equivalentes para teclado o conexión limitada. Ficha: contenido principal y panel lateral de ubicación y fuentes, apilados en móvil. Línea del tiempo: filtro por lugar, año y acceso a ficha. Ruta: indicador de progreso y una parada a la vez. Actividad: radios por pregunta y explicación final. Administración: formularios de Django, sin acceso anónimo de edición.
