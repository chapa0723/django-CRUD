# Panel de Reportes de Tareas

## Resumen

Se ha implementado un sistema completo de reportes para gestionar y analizar las tareas del sistema. El panel permite visualizar estadísticas, filtrar por diferentes criterios y generar reportes específicos.

## Características Implementadas

### 1. Panel Principal de Reportes (`/reports/`)

El panel principal muestra:

#### Estadísticas Generales (Cards)
- **Total de Tareas**: Número total de tareas accesibles
- **Completadas**: Tareas finalizadas
- **Pendientes**: Tareas sin completar
- **Importantes**: Tareas marcadas como importantes

#### Gráficos Visuales
- **Tareas por Estado**: Gráfico de barras que muestra completadas vs pendientes
- **Tareas por Importancia**: Gráfico de barras que muestra importantes vs no importantes

#### Enlaces a Reportes Detallados
- **Creadas Recientes**: Tareas creadas en los últimos 30 días
- **Completadas**: Tareas completadas en los últimos 30 días
- **Por Usuario**: Agrupación de tareas por usuario
- **Por Importancia**: Agrupación de tareas por nivel de importancia
- **Pendientes Antiguas**: Tareas pendientes con más de 30 días

### 2. Reportes Específicos

#### a) Reporte de Tareas Creadas (`/reports/created/`)
- Muestra tareas creadas en un período específico
- Filtro personalizable de días (por defecto 30 días)
- URL: `?days=N` para cambiar el período

**Ejemplo de uso:**
```
/reports/created/?days=15  # Últimos 15 días
/reports/created/?days=60  # Últimos 60 días
```

#### b) Reporte de Tareas Completadas (`/reports/completed/`)
- Muestra tareas completadas en un período específico
- Filtro personalizable de días
- Ordenadas por fecha de finalización

#### c) Reporte Agrupado por Usuario (`/reports/by_user/`)
- Agrupa todas las tareas por usuario
- Muestra estadísticas por usuario:
  - Total de tareas
  - Completadas
  - Pendientes
  - Importantes
  - Barra de progreso de completado

#### d) Reporte Agrupado por Importancia (`/reports/by_importance/`)
- Muestra estadísticas de tareas importantes vs no importantes
- Incluye:
  - Total de tareas por categoría
  - Número de completadas y pendientes
  - Barra de progreso visual

#### e) Reporte de Tareas Pendientes Antiguas (`/reports/old_pending/`)
- Identifica tareas pendientes con más de X días
- Útil para identificar tareas que necesitan atención
- Parámetro: `?days=N` (por defecto 30 días)

### 3. Filtros Dinámicos

Los reportes de fechas soportan filtros dinámicos:
- Campo de entrada para cambiar el número de días
- Botón "Filtrar" para aplicar cambios
- Botón "Resetear" para volver a valores por defecto

### 4. Integración con Permisos

Los reportes respetan el sistema de permisos:
- Solo muestra tareas accesibles al usuario actual
- Incluye tareas propias + tareas compartidas
- Utiliza `get_user_accessible_tasks()` del sistema de permisos

## Estructura de Archivos Creados

```
tasks/
├── reports.py                    # Vistas de reportes
├── templates/
│   ├── reports.html              # Panel principal
│   ├── report_tasks_list.html    # Lista de tareas con filtros
│   ├── report_by_user.html       # Reporte agrupado por usuario
│   └── report_by_importance.html # Reporte por importancia
└── ...

djangocrud/
└── urls.py                        # URLs agregadas
```

## Navegación

Se agregó un enlace al panel de reportes en la barra de navegación:
- Ubicación: Entre "Completadas" y "Nueva"
- Icono: `bi-graph-up`
- Visible solo para usuarios autenticados

## URLs Configuradas

```python
/reports/                          # Panel principal
/reports/created/                  # Tareas creadas
/reports/completed/                # Tareas completadas
/reports/by_user/                  # Por usuario
/reports/by_importance/            # Por importancia
/reports/old_pending/              # Pendientes antiguas
```

## Vistas Disponibles

### tasks.reports.task_reports
Panel principal con estadísticas y enlaces a reportes detallados.

### tasks.reports.report_tasks_created_period
Reporte de tareas creadas en un período.

### tasks.reports.report_tasks_completed_period
Reporte de tareas completadas en un período.

### tasks.reports.report_tasks_by_user
Agrupación de tareas por usuario con estadísticas.

### tasks.reports.report_tasks_by_importance
Agrupación de tareas por importancia con estadísticas.

### tasks.reports.report_old_pending_tasks
Tareas pendientes sin completar desde hace tiempo.

## Tecnologías Utilizadas

- **Django ORM**: Para consultas y agregaciones
- **Bootstrap 5**: Para UI responsive
- **Bootstrap Icons**: Para iconografía
- **SQLite**: Base de datos (configurada previamente)

## Funcionalidades de Agregación

Los reportes utilizan agregaciones de Django ORM:
- `Count()`: Para contar tareas
- `values().annotate()`: Para agrupar por campos
- `filter()`: Para filtrar por fechas y estados
- `order_by()`: Para ordenar resultados

## Ejemplo de Uso

```python
# En el panel de reportes se muestra:
- Total de tareas: 25
- Completadas: 12
- Pendientes: 13
- Importantes: 5

# Al hacer clic en "Por Usuario":
Usuario: admin
Total: 25
Completadas: 12
Pendientes: 13
Importantes: 5

# Al hacer clic en "Creadas Recientes" (30 días):
Tareas creadas en los últimos 30 días: 8
[Lista de tareas con detalles]
```

## Características Adicionales

1. **Filtros Temporales**: Todos los reportes basados en fechas soportan parámetros personalizables
2. **UI Responsive**: Los templates se adaptan a diferentes tamaños de pantalla
3. **Visual Feedback**: Barras de progreso, badges y colores que facilitan la comprensión
4. **Navegación Intuitiva**: Botones "Volver" en todos los reportes detallados

## Próximas Mejoras Sugeridas

1. Exportar reportes a PDF o Excel
2. Gráficos interactivos con Chart.js
3. Exportar datos a CSV
4. Reportes por rangos de fechas personalizados
5. Notificaciones de tareas antiguas
6. Filtros avanzados combinados (fecha + usuario + importancia)

