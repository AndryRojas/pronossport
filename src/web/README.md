# Pronossport Web Dashboard

Interfaz web visual para explorar y analizar los datos de la base de datos `raw_pronossport`.

## Características

### 🏠 Dashboard Principal
- **Estadísticas generales**: Contadores de ligas, países, equipos, jugadores y partidos
- **Gráficos interactivos**: Visualización de países con más ligas y ligas con más equipos
- **Accesos rápidos**: Enlaces directos a las diferentes secciones

### 🏆 Ligas
- **Visualización completa**: Todas las ligas agrupadas por país
- **Filtros avanzados**: Por temporada y país
- **Vistas múltiples**: Tabla detallada o tarjetas visuales
- **Información completa**: Logos, banderas, fechas de temporada, IDs externos

### ⚽ Equipos
- **Exploración de equipos**: Por liga, temporada y país
- **Detalles del equipo**: Logos, estadios, ubicaciones
- **Conteo de jugadores**: Número de jugadores por equipo
- **Enlaces rápidos**: Acceso directo a jugadores y partidos

### 👥 Jugadores
- **Base de datos de jugadores**: Búsqueda por equipo, liga y temporada
- **Perfiles completos**: Fotos, posiciones, nacionalidades, medidas físicas
- **Información detallada**: Edad, número de camiseta, estadísticas básicas
- **Filtros múltiples**: Por equipo, liga o temporada

### 📅 Partidos
- **Historial de partidos**: Filtrable por liga, temporada y fechas
- **Resultados en tiempo real**: Estados de partidos (finalizado, en vivo, programado)
- **Detalles del encuentro**: Equipos, resultados, estadios, jornadas
- **Vista cronológica**: Ordenados por fecha más reciente

### ⚙️ Administración de datos
- **Análisis de completitud**: Identificación de datos faltantes en la base de datos
- **Tabla Ligas-Equipos-Partidos**: Vista consolidada de todas las ligas con conteos de equipos y partidos
- **Tabla Equipos-Jugadores**: Vista detallada de equipos por liga con conteo de jugadores
- **Filtros especializados**: "Todos" vs "Sin dato" para identificar información faltante
- **Navegación integrada**: Enlaces directos para completar datos faltantes
- **Estadísticas de resumen**: Contadores de completitud de datos

## Arquitectura Técnica

### Backend (Flask)
- **Framework**: Flask 3.0 con extensiones
- **Base de datos**: SQLAlchemy ORM conectado a MySQL
- **APIs**: Endpoints REST para datos JSON
- **Servicios**: Capa de servicios especializada para consultas web

### Frontend
- **UI Framework**: Bootstrap 5.3 con iconos
- **JavaScript**: Vanilla JS con funcionalidades avanzadas
- **Gráficos**: Chart.js para visualizaciones
- **Responsive**: Diseño adaptable a móviles y escritorio

### Estructura de Archivos

```
src/web/
├── app.py                 # Aplicación Flask principal
├── templates/             # Templates HTML
│   ├── base.html         # Template base
│   ├── index.html        # Dashboard principal
│   ├── leagues.html      # Página de ligas
│   ├── teams.html        # Página de equipos
│   ├── players.html      # Página de jugadores
│   ├── matches.html      # Página de partidos
│   └── error.html        # Página de errores
├── static/               # Archivos estáticos
│   ├── css/
│   │   └── dashboard.css # Estilos personalizados
│   └── js/
│       └── dashboard.js  # JavaScript funcional
└── api/                  # Endpoints API (futuro)
```

## Comandos de Uso

### Iniciar el Dashboard Web

```bash
# Comando básico
python main.py web-dashboard

# Con opciones personalizadas
python main.py web-dashboard --host 0.0.0.0 --port 8080 --debug

# Abrir navegador automáticamente
python main.py web-dashboard --auto-open

# Modo desarrollo con auto-reload
python main.py web-dashboard --debug --auto-open
```

### Opciones Disponibles

- `--host`: Host del servidor (default: 0.0.0.0)
- `--port`: Puerto del servidor (default: 5000)
- `--debug`: Modo debug con auto-reload
- `--auto-open`: Abrir navegador automáticamente

## Instalación y Configuración

### 1. Dependencias
Asegúrate de tener instaladas las dependencias web:

```bash
pip install flask==3.0.0 flask-cors==4.0.0
```

O instala todas las dependencias:

```bash
pip install -r requirements.txt
```

### 2. Base de Datos
El dashboard requiere acceso a la base de datos `raw_pronossport`. Configura tu archivo `.env`:

```env
# Base de datos raw_pronossport
RAW_DB_HOST=localhost
RAW_DB_PORT=3306
RAW_DB_USER=tu_usuario
RAW_DB_PASSWORD=tu_password
RAW_DB_NAME=raw_pronossport
```

### 3. Verificación
Prueba la conexión antes de iniciar el dashboard:

```bash
python main.py test-connections
```

## Funcionalidades Avanzadas

### 🔍 Búsqueda y Filtros
- **Filtros dinámicos**: Se aplican automáticamente al cambiar selecciones
- **Búsqueda en tiempo real**: En tablas y listas
- **Múltiples criterios**: Combinación de filtros por diferentes campos

### 📊 Visualizaciones
- **Gráficos interactivos**: Con Chart.js para estadísticas
- **Vistas alternativas**: Tabla vs tarjetas
- **Información contextual**: Tooltips y detalles al hover

### 🎨 Interfaz de Usuario
- **Diseño responsive**: Adaptado a móviles y tablets
- **Tema moderno**: Basado en Bootstrap 5
- **Iconografía**: Bootstrap Icons para mejor UX
- **Animaciones suaves**: Transiciones y efectos visuales

### ⚡ Performance
- **Paginación**: Límites en consultas grandes (1000 registros)
- **Lazy loading**: Carga progresiva de imágenes
- **Caché inteligente**: Optimización de consultas frecuentes

## API Endpoints

### Endpoints de Datos
- `GET /api/leagues` - Obtener ligas con filtros
- `GET /api/teams` - Obtener equipos con filtros  
- `GET /api/players` - Obtener jugadores con filtros
- `GET /api/matches` - Obtener partidos con filtros
- `GET /api/stats` - Estadísticas del dashboard

### Parámetros de Filtro
- `season`: Filtrar por temporada
- `country`: Filtrar por país
- `league_id`: Filtrar por liga
- `team_id`: Filtrar por equipo
- `date_from`: Fecha desde (partidos)
- `date_to`: Fecha hasta (partidos)

## Desarrollo y Personalización

### Agregar Nuevas Páginas
1. Crear template en `templates/`
2. Agregar ruta en `app.py`
3. Implementar servicio en `web_query_service.py`
4. Actualizar navegación en `base.html`

### Modificar Estilos
- Editar `static/css/dashboard.css`
- Usar variables CSS para consistencia
- Mantener responsive design

### Agregar Funcionalidades JavaScript
- Extender `static/js/dashboard.js`
- Usar funciones modulares
- Mantener compatibilidad cross-browser

## Troubleshooting

### Problemas Comunes

1. **Error de conexión a base de datos**
   - Verificar configuración en `.env`
   - Ejecutar `python main.py test-connections`

2. **Página en blanco o errores 500**
   - Revisar logs con `--debug`
   - Verificar que existan datos en las tablas

3. **Estilos no se cargan**
   - Verificar que existe `static/css/dashboard.css`
   - Limpiar caché del navegador

4. **JavaScript no funciona**
   - Verificar consola del navegador para errores
   - Asegurarse de que Bootstrap JS esté cargado

### Logs y Debug
```bash
# Modo debug con logs detallados
python main.py web-dashboard --debug

# Verificar estado del sistema
python main.py status
```

## Contribuir

Para contribuir al dashboard web:

1. Mantener consistencia con el diseño existente
2. Documentar nuevas funcionalidades
3. Probar en diferentes navegadores
4. Optimizar performance de consultas
5. Seguir las convenciones de código Python/JavaScript

## Roadmap Futuro

- [ ] Exportación de datos (CSV, Excel)
- [ ] Filtros guardados y favoritos
- [ ] Dashboard personalizable con widgets
- [ ] Notificaciones en tiempo real
- [ ] API completa para integraciones externas
- [ ] Modo offline con service workers
- [ ] Temas oscuro/claro
- [ ] Comparación de estadísticas
- [ ] Reportes automáticos