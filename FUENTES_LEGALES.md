# EKSLENS - FUENTES LEGALES DE DATOS

## ⚖️ Cumplimiento Legal

### LinkedIn - TEMPORALMENTE DESHABILITADO
- **Estado**: ❌ Deshabilitado por políticas de uso
- **Razón**: LinkedIn prohíbe explícitamente el scraping automatizado
- **Acción**: Consultando sobre API oficial o términos de uso
- **Alternativa**: Usar fuentes legales listadas abajo

## 🔍 Fuentes Legales Recomendadas

### 1. SerpAPI (✅ IMPLEMENTADO)
- **Descripción**: API oficial para búsquedas en Google, Bing, etc.
- **Legal**: ✅ Completamente legal con términos de servicio claros
- **Configuración**: API Key en `SERPAPI_KEY` (.env)
- **URL**: https://serpapi.com/
- **Uso**: Búsqueda de empresas, sitios web, información pública

### 2. Google My Business API
- **Descripción**: API oficial de Google para información de negocios
- **Legal**: ✅ API oficial de Google
- **Datos**: Información de negocios, ubicaciones, reviews
- **URL**: https://developers.google.com/my-business
- **Estado**: 🔄 A implementar

### 3. Yelp API  
- **Descripción**: API para información de negocios locales
- **Legal**: ✅ API oficial
- **Datos**: Información empresarial, reviews, contactos
- **URL**: https://www.yelp.com/developers
- **Estado**: 🔄 A implementar

### 4. Yellow Pages API
- **Descripción**: Directorio comercial con API pública
- **Legal**: ✅ API oficial
- **Datos**: Información empresarial, contactos
- **Estado**: 🔄 A implementar

### 5. OpenCorporates API
- **Descripción**: Base de datos pública de empresas
- **Legal**: ✅ Datos públicos con API oficial
- **Datos**: Información corporativa, directivos
- **URL**: https://opencorporates.com/
- **Estado**: 🔄 A implementar

### 6. Clearbit API
- **Descripción**: API para información empresarial y contactos
- **Legal**: ✅ API oficial con cumplimiento GDPR
- **Datos**: Emails empresariales, información de empresas
- **URL**: https://clearbit.com/
- **Estado**: 🔄 A implementar

## 🚫 Fuentes NO Recomendadas

### Scraping Directo
- ❌ LinkedIn scraping (políticas estrictas)
- ❌ Facebook/Instagram scraping (términos de servicio)
- ❌ Sitios web sin autorización explícita
- ❌ Directorios con protección anti-bot

## 📋 Plan de Implementación

### Fase 1 - Fuentes Principales (ACTUAL)
- [x] SerpAPI (Google, Bing, etc.)
- [ ] Mejorar SerpAPI para más tipos de búsqueda
- [ ] Optimizar keywords por industria

### Fase 2 - APIs Empresariales
- [ ] Google My Business API
- [ ] Yelp API
- [ ] Yellow Pages API

### Fase 3 - APIs Especializadas
- [ ] OpenCorporates API
- [ ] Clearbit API
- [ ] APIs específicas por país/región

## 🔧 Configuración Actual

### Variables de Entorno Requeridas (.env)
```
# SerpAPI (Principal)
SERPAPI_KEY=tu_serpapi_key_aqui

# APIs Adicionales (Futuro)
GOOGLE_BUSINESS_API_KEY=tu_google_business_key
YELP_API_KEY=tu_yelp_key
CLEARBIT_API_KEY=tu_clearbit_key
```

### Uso Recomendado
```python
# Usar solo fuentes legales
results = coordinator.run_master_search_with_keywords(
    keywords=['botox', 'medicina estética'],
    cities=['madrid'],
    use_serpapi=True,      # ✅ Legal
    use_linkedin=False,    # ❌ Deshabilitado
    use_instagram=False    # ❌ Deshabilitado temporalmente
)
```

## 📊 Comparación de Fuentes

| Fuente | Legal | Coste | Calidad Datos | Implementado |
|--------|-------|--------|---------------|--------------|
| SerpAPI | ✅ | Medio | Alta | ✅ |
| Google Business | ✅ | Gratis/Cuotas | Alta | 🔄 |
| Yelp API | ✅ | Gratis/Cuotas | Media | 🔄 |
| LinkedIn API | ✅ | Caro | Muy Alta | ❌ Solo para partners |
| LinkedIn Scraping | ❌ | Gratis | Alta | ❌ Prohibido |

## 📞 Contacto Legal

Si necesitas acceso a LinkedIn:
- Contacta LinkedIn Developer Program
- Solicita LinkedIn Marketing Developer Platform
- Considera LinkedIn Sales Navigator (uso manual)

**Recuerda**: Siempre respetar términos de servicio y políticas de privacidad.