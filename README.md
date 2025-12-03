# 🔍 EKSLENS - Sistema Inteligente de Captación de Leads

**Sistema avanzado de generación de leads** que demuestra la integración profesional de múltiples tecnologías: **Web Scraping**, **APIs REST**, **Bases de Datos PostgreSQL** e **Inteligencia Artificial**.

Diseñado específicamente para el sector de medicina estética, EKSLENS automatiza la búsqueda, validación y gestión de contactos comerciales potenciales a través de múltiples fuentes de datos.

---

## 🎯 Objetivo del Proyecto

Este proyecto es una **demostración técnica integral** que muestra:

- **Integración de Base de Datos**: PostgreSQL con funciones PL/pgSQL para lógica de negocio
- **Consumo de APIs**: Google Gemini AI, SerpApi para búsquedas web
- **Web Scraping**: Extracción automatizada y ética de datos públicos
- **Arquitectura Modular**: Diseño escalable por industrias
- **Frontend Interactivo**: Interfaz web con estadísticas en tiempo real

---

## 🏗️ Arquitectura Técnica

### **Stack Tecnológico**

```
Backend:
├── Python 3.9+
├── PostgreSQL 13+ (Base de datos relacional)
├── Flask (API REST)
└── psycopg2 (Driver PostgreSQL)

APIs Externas:
├── Google Gemini AI (Generación de contenido)
├── SerpApi (Búsquedas en Google)
└── LinkedIn API (Opcional)

Web Scraping:
├── BeautifulSoup4
├── Selenium
└── Requests

Frontend:
├── HTML5/CSS3
├── JavaScript Vanilla
└── Font Awesome Icons
```

### **Componentes Principales**

```
ekslens/
│
├── database.py              # Capa de abstracción de PostgreSQL
├── web_interface.py         # API REST con Flask
├── ekslens_lead_master_modular.py  # Coordinador principal
│
├── scrapers/
│   ├── serpapi_scraper.py   # Integración con SerpApi
│   └── linkedin_scraper.py  # Scraping de LinkedIn (opcional)
│
├── industries/
│   ├── base_industry.py     # Clase base para industrias
│   ├── medical_aesthetics.py # Configuración medicina estética
│   └── real_estate.py       # Ejemplo de extensibilidad
│
└── templates/
    └── index.html           # Dashboard interactivo
```

---

## ✨ Características Principales

### 🔍 **1. Web Scraping Inteligente**
- Extracción automatizada de datos desde múltiples fuentes
- Validación de datos con filtros específicos por industria
- Respeto de políticas robots.txt y rate limiting
- Detección y manejo de CAPTCHAs

### 🗄️ **2. Gestión de Base de Datos**
- **Schema relacional** optimizado para leads comerciales
- **Funciones PL/pgSQL** para lógica de negocio en BD
- **Tracking de fuentes** para análisis de ROI
- **Queries optimizadas** con índices y vistas materializadas

### 🤖 **3. Integración con IA**
- **Google Gemini AI** para generación de emails personalizados
- Análisis de contexto para mensajes relevantes
- Adaptación automática según perfil del lead

### 📊 **4. Dashboard Analítico**
- Estadísticas en tiempo real
- Visualización por fuentes de leads
- Consultas SQL personalizadas desde UI
- Exportación de datos

### 🔌 **5. API REST**
- Endpoints para CRUD de leads
- Búsquedas programáticas
- Cambio dinámico de industria
- Respuestas JSON estructuradas

---

## 🚀 Instalación y Configuración

### **Prerrequisitos**

```bash
- Python 3.9 o superior
- PostgreSQL 13 o superior
- pip (gestor de paquetes Python)
- Git
```

### **1. Clonar el Repositorio**

```bash
git clone https://github.com/Ciclope988/Proyecto-Final-hack-a-boss.git
cd Proyecto-Final-hack-a-boss
```

### **2. Crear Entorno Virtual**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### **3. Instalar Dependencias**

```bash
pip install -r requirements.txt
```

### **4. Configurar Base de Datos PostgreSQL**

```sql
-- Crear base de datos
CREATE DATABASE ekslens_leads;

-- Conectar y crear esquema
\c ekslens_leads

-- Ejecutar script de creación de tablas
\i setup_database.sql
```

### **5. Configurar Variables de Entorno**

```bash
# Copiar template de configuración
cp .env.example .env

# Editar .env con tus credenciales
nano .env
```

**Variables obligatorias:**
```env
GOOGLE_API_KEY=tu_api_key_de_gemini
SERPAPI_KEY=tu_api_key_de_serpapi
DATABASE_URL=postgresql://user:password@localhost:5433/ekslens_leads
```

### **6. Ejecutar el Sistema**

```bash
# Opción 1: Interfaz Web (Recomendado)
python web_interface.py
# Acceder a: http://localhost:5000

# Opción 2: Línea de comandos
python ekslens_lead_master_modular.py
```

---

## 💡 Casos de Uso

### **Búsqueda Automática de Leads**

```python
from ekslens_lead_master_modular import EkslensLeadMaster

# Inicializar con industria específica
lead_master = EkslensLeadMaster('medical_aesthetics')

# Ejecutar búsqueda
results = lead_master.search_leads(
    cities=['Madrid', 'Barcelona'],
    keywords=['clínica estética', 'medicina estética'],
    max_searches=5
)

print(f"Leads encontrados: {len(results)}")
```

### **Agregar Leads Manualmente**

```python
from database import Database

db = Database()
lead_id = db.save_manual_linkedin_lead(
    nombre="Dr. María López",
    email="maria@clinica.com",
    telefono="+34 123 456 789",
    linkedin_url="https://linkedin.com/in/maria-lopez",
    description="Directora de clínica estética en Madrid"
)
```

### **Consultas SQL Personalizadas**

```python
# Obtener leads por fuente
results = db.execute_query("""
    SELECT source, COUNT(*) as total
    FROM leads
    GROUP BY source
    ORDER BY total DESC
""")
```

---

## 🔧 Arquitectura de Base de Datos

### **Tablas Principales**

#### **`leads`** - Tabla central de contactos
```sql
CREATE TABLE leads (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    telefono VARCHAR(50),
    linkedin_url VARCHAR(500),
    website VARCHAR(500),
    description TEXT,
    source VARCHAR(100) NOT NULL,  -- 'SerpApi', 'LinkedIn (Manual)', etc.
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Índices optimizados
    INDEX idx_source (source),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);
```

#### **Función PL/pgSQL Ejemplo**
```sql
CREATE OR REPLACE FUNCTION save_manual_linkedin_lead(
    p_nombre VARCHAR,
    p_email VARCHAR DEFAULT NULL,
    p_telefono VARCHAR DEFAULT NULL,
    p_linkedin_url VARCHAR DEFAULT NULL,
    p_description TEXT DEFAULT NULL
) RETURNS JSON AS $$
DECLARE
    new_lead_id INTEGER;
BEGIN
    INSERT INTO leads (nombre, email, telefono, linkedin_url, description, source)
    VALUES (p_nombre, p_email, p_telefono, p_linkedin_url, p_description, 'LinkedIn (Manual)')
    RETURNING id INTO new_lead_id;
    
    RETURN json_build_object('success', true, 'lead_id', new_lead_id);
END;
$$ LANGUAGE plpgsql;
```

---

## 📡 API REST Endpoints

### **Gestión de Leads**

```bash
# Agregar lead manual
POST /api/add_manual_lead
Content-Type: application/json
{
    "nombre": "Juan Pérez",
    "email": "juan@example.com",
    "telefono": "+34 600 000 000",
    "linkedin_url": "https://linkedin.com/in/juan"
}

# Obtener estadísticas
GET /api/database_stats

# Ejecutar consulta personalizada
POST /api/execute_query
Content-Type: application/json
{
    "query": "SELECT * FROM leads WHERE source = 'SerpApi' LIMIT 10"
}
```

### **Control de Búsquedas**

```bash
# Iniciar búsqueda
POST /api/start_search
{
    "cities": ["Madrid", "Barcelona"],
    "keywords": ["clínica", "medicina estética"],
    "max_searches": 3
}

# Verificar estado
GET /api/status

# Obtener logs en tiempo real
GET /api/logs
```

---

## 🎨 Extensibilidad - Sistema Modular por Industrias

El sistema está diseñado para ser **fácilmente extensible** a otras industrias:

### **Crear Nueva Industria**

```python
# industries/tu_industria.py
from industries.base_industry import BaseIndustry

class TuIndustria(BaseIndustry):
    def __init__(self):
        super().__init__(
            name="Tu Industria",
            search_terms=["término1", "término2"],
            keywords=["keyword1", "keyword2"]
        )
    
    def validate_lead(self, lead_data):
        # Lógica específica de validación
        return True
    
    def get_serpapi_params(self, keyword, location):
        # Parámetros personalizados para búsquedas
        return {
            'q': f'{keyword} {location}',
            'location': location,
            'hl': 'es',
            'gl': 'es'
        }
```

---

## 🛡️ Seguridad y Buenas Prácticas

### **Protección de Credenciales**
- ✅ Archivo `.env` incluido en `.gitignore`
- ✅ Template `.env.example` para documentación
- ✅ Sin credenciales hardcodeadas en código

### **Web Scraping Ético**
- ✅ Respeto de `robots.txt`
- ✅ Rate limiting entre requests
- ✅ User-Agent identificable
- ✅ Manejo de errores y timeouts

### **Base de Datos**
- ✅ Queries parametrizadas (prevención SQL injection)
- ✅ Conexiones seguras con pool
- ✅ Validación de inputs
- ✅ Logging de operaciones

---

## 📊 Métricas del Sistema

### **Capacidades**
- 🔍 **Búsquedas**: Hasta 100 leads/búsqueda
- 📈 **Rendimiento**: ~50 leads/minuto (depende de APIs)
- 💾 **Almacenamiento**: Sin límite (PostgreSQL escalable)
- 🌐 **Multi-ciudad**: Soporte para múltiples ubicaciones simultáneas

### **Tracking de ROI**
El sistema permite trackear la fuente de cada lead:
- `SerpApi` - Búsquedas automáticas en Google
- `LinkedIn (Manual)` - Contactos agregados manualmente
- `Instagram` - Scraping de redes sociales
- `Referral` - Referencias directas

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add: nueva característica'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📝 Roadmap

### **Versión 2.1** (En desarrollo)
- [ ] Integración con Bing Search API
- [ ] Export a CSV/Excel
- [ ] Notificaciones por email automáticas
- [ ] Dashboard con gráficos avanzados

### **Versión 3.0** (Planeado)
- [ ] Machine Learning para scoring de leads
- [ ] Integración con CRMs externos (HubSpot, Salesforce)
- [ ] App móvil (React Native)
- [ ] Autenticación multi-usuario

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

---

## 👤 Autor

**Agustin Trebucq**
- GitHub: [@Ciclope988](https://github.com/Ciclope988)
- Proyecto: [Proyecto-Final-hack-a-boss](https://github.com/Ciclope988/Proyecto-Final-hack-a-boss)

---

## 🙏 Agradecimientos

- **Google Gemini AI** por la API de generación de contenido
- **SerpApi** por el acceso a búsquedas de Google
- Comunidad de **PostgreSQL** por la excelente documentación
- Stack Overflow y la comunidad open-source

---

## ⚠️ Disclaimer

Este proyecto es una **demostración técnica** con fines educativos. El web scraping debe realizarse respetando:
- Términos de servicio de cada plataforma
- Leyes de protección de datos (GDPR, LOPD)
- Políticas robots.txt
- Rate limits de APIs

**Uso responsable y ético obligatorio.**

---

<div align="center">

**🔍 EKSLENS** - *Transformando la búsqueda de leads con tecnología*

⭐ Si te ha gustado el proyecto, ¡déjanos una estrella en GitHub!

</div>