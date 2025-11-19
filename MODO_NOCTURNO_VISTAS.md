# Modo Nocturno y Sistema de Vistas

## Resumen

Se ha implementado un sistema completo de modo nocturno (dark mode) y alternancia entre vista de lista y tarjetas para mejorar la experiencia del usuario.

## Características Implementadas

### 1. **Modo Nocturno / Modo Diurno**

#### Funcionalidad
- Botón en la barra de navegación global para cambiar entre modo claro y oscuro
- Persistencia de preferencia usando `localStorage`
- El tema se mantiene al navegar entre páginas
- Icono que cambia según el tema actual:
  - 🌙 Luna = modo claro disponible
  - ☀️ Sol = modo oscuro activo

#### Estilos Aplicados
El modo oscuro incluye:
- Fondo oscuro (#121212)
- Texto claro (#e0e0e0)
- Tarjetas con fondo oscuro (#2d2d2d)
- Bordes suaves (#404040)
- Ajustes de contraste para mejor legibilidad
- Compatibilidad con todos los componentes Bootstrap

#### Ubicación del Botón
- **Navbar global**: Disponible en todas las páginas
- **Página de Tareas**: Botón adicional junto a los controles de vista

### 2. **Vista de Lista vs Vista de Tarjetas**

#### Funcionalidad
- Grupo de botones para alternar entre vistas
- Persistencia de preferencia usando `localStorage`
- Transiciones suaves al cambiar de vista

#### Vista de Tarjetas (Grid)
- Layout en cuadrícula responsiva
- Mínimo 300px por tarjeta
- Distribución automática según ancho de pantalla
- Ideal para exploración visual

#### Vista de Lista
- Layout en una sola columna
- Tarjetas alineadas horizontalmente
- Información más compacta
- Ideal para búsqueda y lectura rápida
- Adaptación responsive en móviles

#### Características
- Responsive: Se adapta automáticamente a móviles
- Cards flexibles en ambas vistas
- Misma información en ambas vistas
- Transiciones suaves

### 3. **Persistencia de Preferencias**

Ambas funcionalidades utilizan `localStorage` del navegador:

```javascript
// Tema
localStorage.getItem('theme') // 'dark' o 'light'
localStorage.setItem('theme', 'dark')

// Vista
localStorage.getItem('viewMode') // 'grid' o 'list'
localStorage.setItem('viewMode', 'list')
```

Las preferencias se mantienen entre sesiones y páginas.

## Archivos Modificados

### 1. `tasks/templates/tasks.html`
- Agregados botones para cambiar tema y vista
- Estilos CSS para modo oscuro
- Estilos CSS para vistas lista/grid
- JavaScript para gestionar preferencias

### 2. `tasks/templates/_navbar.html`
- Agregado botón global de cambio de tema
- JavaScript global para sincronizar tema

### 3. `tasks/templates/base.html`
- Estilos globales para modo oscuro
- Script para aplicar tema al cargar la página

## Instrucciones de Uso

### Cambiar Tema

1. **Desde cualquier página**: Haz clic en el botón 🌙/☀️ en la barra de navegación
2. **Solo página de tareas**: Botón adicional junto a los controles de vista
3. El tema se aplica inmediatamente a toda la página
4. La preferencia se guarda automáticamente

### Cambiar Vista

1. Ve a la página de "Tareas"
2. Encuentra los botones de vista junto al título
3. Haz clic en:
   - 📊 Grid: Vista de tarjetas
   - 📋 List: Vista de lista
4. La preferencia se guarda automáticamente

## Tecnologías Utilizadas

- **JavaScript vanilla**: Sin dependencias externas
- **localStorage API**: Para persistencia
- **CSS Grid & Flexbox**: Para layouts
- **Bootstrap Icons**: Para iconografía
- **Media Queries**: Para responsive

## Ejemplo de Código

### Cambio de Tema
```javascript
// Verificar tema guardado
const savedTheme = localStorage.getItem('theme') || 'light';

// Aplicar tema
if (savedTheme === 'dark') {
  document.body.classList.add('dark-mode');
}

// Cambiar tema
themeToggle.addEventListener('click', function() {
  document.body.classList.toggle('dark-mode');
  localStorage.setItem('theme', 
    document.body.classList.contains('dark-mode') ? 'dark' : 'light'
  );
});
```

### Cambio de Vista
```javascript
// Verificar vista guardada
const savedView = localStorage.getItem('viewMode') || 'grid';

// Aplicar vista
tasksContainer.classList.add(savedView === 'list' ? 'list-view' : 'grid-view');

// Cambiar vista
viewBtn.addEventListener('click', function() {
  tasksContainer.classList.toggle('list-view');
  localStorage.setItem('viewMode', 
    tasksContainer.classList.contains('list-view') ? 'list' : 'grid'
  );
});
```

## Responsive Design

Ambas funcionalidades son completamente responsive:
- En móviles, la vista de lista se adapta verticalmente
- Los botones se mantienen accesibles en todas las resoluciones
- El modo oscuro funciona perfectamente en cualquier dispositivo

## Notas Técnicas

1. **Sin dependencias**: Todo funciona con JavaScript vanilla y CSS
2. **Performance**: Cambios instantáneos, sin recargar la página
3. **Compatibilidad**: Funciona en todos los navegadores modernos
4. **Accesibilidad**: Iconos descriptivos y estados visuales claros

## Próximas Mejoras Sugeridas

1. Animaciones más elaboradas en las transiciones
2. Múltiples temas predefinidos (no solo claro/oscuro)
3. Personalización de colores por el usuario
4. Exportar preferencias a cuenta de usuario
5. Detección automática del tema del sistema operativo

