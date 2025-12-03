"""
EKSLENS - SerpApi Scraper
Scraper especializado para búsquedas SerpApi
"""

import time
import logging
from typing import List, Dict, Optional
from datetime import datetime
from industries.base_industry import BaseIndustry

try:
    from serpapi import GoogleSearch
except ImportError:
    GoogleSearch = None

logger = logging.getLogger(__name__)


class SerpApiScraper:
    """Scraper especializado para SerpApi con configuración por industria."""
    
    def __init__(self, api_key: str, industry: BaseIndustry):
        self.api_key = api_key
        self.industry = industry
        self.available = GoogleSearch is not None and api_key
        
        if not self.available:
            logger.warning("SerpApi no disponible - falta API key o librería")
    
    def search_by_keywords(self, cities: List[str], keywords: List[str], max_searches: int = 3) -> List[Dict]:
        """Ejecutar búsquedas SerpApi con keywords personalizadas."""
        if not self.available:
            print("⚠️ SerpApi no disponible")
            return []
        
        leads = []
        search_count = 0
        
        print(f"\n🔍 INICIANDO SERPAPI SCRAPER")
        print(f"📋 Industria: {self.industry.name}")
        print(f"🎯 Keywords: {', '.join(keywords[:3])}{'...' if len(keywords) > 3 else ''}")
        
        try:
            # Combinar ciudades y keywords
            for city in cities:
                if search_count >= max_searches:
                    break
                
                for keyword in keywords:
                    if search_count >= max_searches:
                        break
                    
                    print(f"\n🔎 Búsqueda {search_count + 1}/{max_searches}")
                    print(f"   📍 Ciudad: {city}")
                    print(f"   🎯 Keyword: {keyword}")
                    
                    # Obtener parámetros optimizados por industria
                    search_params = self.industry.get_serpapi_params(keyword, city)
                    search_params['api_key'] = self.api_key
                    
                    # Ejecutar búsqueda
                    search_results = self._execute_search(search_params)
                    
                    if search_results:
                        city_leads = self._process_results(search_results, keyword, city)
                        leads.extend(city_leads)
                        print(f"   ✅ {len(city_leads)} leads encontrados")
                    else:
                        print(f"   ❌ Sin resultados")
                    
                    search_count += 1
                    time.sleep(2)  # Rate limiting
            
        except Exception as e:
            logger.error(f"Error en SerpApi scraper: {e}")
            print(f"❌ Error en SerpApi: {e}")
        
        print(f"\n📊 SerpApi completado: {len(leads)} leads totales")
        return leads
    
    def _execute_search(self, params: Dict) -> Optional[Dict]:
        """Ejecutar búsqueda individual en SerpApi."""
        try:
            search = GoogleSearch(params)
            results = search.get_dict()
            
            if "organic_results" in results:
                return results
            else:
                logger.warning("No hay resultados orgánicos en la respuesta")
                return None
                
        except Exception as e:
            logger.error(f"Error ejecutando búsqueda SerpApi: {e}")
            return None
    
    def _process_results(self, results: Dict, keyword: str, city: str) -> List[Dict]:
        """Procesar y filtrar resultados de SerpApi."""
        leads = []
        
        for result in results.get("organic_results", [])[:5]:  # Máximo 5 por búsqueda
            lead_data = {
                'name': result.get('title', ''),
                'website': result.get('link', ''),
                'description': result.get('snippet', ''),
                'source': 'SerpApi',
                'keyword': keyword,
                'city': city,
                'search_term': f"{keyword} {city}",
                'found_date': datetime.now(),
                'industry': self.industry.name
            }
            
            # Validar con filtros de la industria
            if self.industry.validate_lead(lead_data):
                leads.append(lead_data)
            else:
                print(f"   ⚠️ Lead filtrado: {lead_data['name'][:30]}...")
        
        return leads
    
    def get_monthly_usage(self) -> Dict:
        """Obtener información de uso mensual de SerpApi."""
        if not self.available:
            return {'searches_used': 0, 'searches_remaining': 0}
        
        try:
            # Búsqueda de prueba para obtener créditos
            test_search = GoogleSearch({
                'q': 'test',
                'api_key': self.api_key,
                'num': 1
            })
            
            results = test_search.get_dict()
            credits_info = results.get('credits_info', {})
            
            return {
                'searches_used': credits_info.get('monthly_searches_used', 0),
                'searches_remaining': credits_info.get('monthly_searches_left', 100),
                'monthly_limit': credits_info.get('monthly_search_limit', 100)
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo uso de SerpApi: {e}")
            return {'searches_used': 0, 'searches_remaining': 100}