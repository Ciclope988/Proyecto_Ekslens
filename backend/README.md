# EKSLENS Backend

Arquitectura modularizada del backend de EKSLENS.

## Estructura

```
backend/
├── api/                    # API REST endpoints
│   ├── routes.py          # Rutas Flask
│   └── __init__.py
├── config/                 # Configuraciones
│   ├── settings.py        # Configuración general
│   └── __init__.py
├── database/               # Capa de base de datos
│   ├── connection.py      # Conexión PostgreSQL
│   ├── models.py          # Esquemas de tablas
│   ├── queries.py         # Operaciones CRUD
│   └── __init__.py
├── services/               # Lógica de negocio
│   ├── lead_service.py    # Servicio de leads
│   ├── search_service.py  # Servicio de búsquedas
│   └── __init__.py
└── utils/                  # Utilidades
    ├── helpers.py         # Funciones auxiliares
    └── __init__.py
```

## Componentes

### API (`backend/api/`)
- **routes.py**: Define todos los endpoints REST (Flask Blueprints)
- Separación en blueprints `api_bp` (API) y `web_bp` (vistas web)

### Config (`backend/config/`)
- **settings.py**: Configuración centralizada de la aplicación
- Base de datos, Flask, APIs externas, logging

### Database (`backend/database/`)
- **connection.py**: Gestión de conexión PostgreSQL
- **models.py**: Definición de esquemas de tablas
- **queries.py**: Operaciones CRUD y consultas complejas

### Services (`backend/services/`)
- **lead_service.py**: Lógica de negocio para leads
- **search_service.py**: Lógica de búsquedas y procesamiento asíncrono

### Utils (`backend/utils/`)
- **helpers.py**: Funciones auxiliares reutilizables
- Formateo de datos, validaciones, utilidades generales

## Uso

```python
from backend.api.routes import api_bp, web_bp
from backend.services.lead_service import LeadService
from backend.database.queries import DatabaseQueries

# Usar servicios
lead_service = LeadService()
stats = lead_service.get_database_stats()

# Usar base de datos directamente
db = DatabaseQueries()
leads = db.get_leads(limit=10)
```

## Ventajas de esta arquitectura

1. **Separación de responsabilidades**: Cada módulo tiene un propósito claro
2. **Mantenibilidad**: Código organizado y fácil de mantener
3. **Escalabilidad**: Fácil añadir nuevos endpoints o servicios
4. **Testabilidad**: Componentes independientes más fáciles de testear
5. **Reutilización**: Servicios y utilidades reutilizables
