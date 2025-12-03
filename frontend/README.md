# EKSLENS Frontend

Interfaz de usuario separada del backend.

## Estructura

```
frontend/
├── static/              # Archivos estáticos
│   ├── css/            # Estilos CSS
│   └── js/             # JavaScript
└── templates/           # Plantillas HTML
    └── index.html      # Dashboard principal
```

## Tecnologías

- **HTML5**: Estructura de la aplicación web
- **CSS3**: Estilos (Font Awesome para iconos)
- **JavaScript**: Lógica del cliente
- **Flask Templates**: Renderizado server-side

## Características

- Dashboard interactivo para gestión de leads
- Formulario de búsqueda con múltiples parámetros
- Panel de estadísticas en tiempo real
- Consultas SQL personalizadas
- Logs de ejecución en tiempo real

## Futura modularización

En próximas versiones, se separará:
- CSS embebido → `static/css/styles.css`
- JavaScript embebido → `static/js/dashboard.js`
- Componentes reutilizables
