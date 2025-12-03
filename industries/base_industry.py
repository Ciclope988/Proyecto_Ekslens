"""
EKSLENS - Base Industry Configuration
Clase base para configuraciones de industrias específicas
"""

from typing import List, Dict, Optional
from abc import ABC, abstractmethod


class BaseIndustry(ABC):
    """Clase base para configuraciones de industrias específicas."""
    
    def __init__(self):
        self.name = self.get_industry_name()
        self.keywords = self.get_default_keywords()
        self.search_terms = self.get_search_terms()
        self.filters = self.get_search_filters()
    
    @abstractmethod
    def get_industry_name(self) -> str:
        """Nombre de la industria."""
        pass
    
    @abstractmethod
    def get_default_keywords(self) -> List[str]:
        """Keywords por defecto para esta industria."""
        pass
    
    @abstractmethod
    def get_search_terms(self) -> List[str]:
        """Términos de búsqueda especializados."""
        pass
    
    @abstractmethod
    def get_search_filters(self) -> Dict:
        """Filtros específicos de búsqueda."""
        pass
    
    @abstractmethod
    def get_company_indicators(self) -> List[str]:
        """Indicadores que identifican empresas relevantes."""
        pass
    
    @abstractmethod
    def validate_lead(self, lead_data: Dict) -> bool:
        """Validar si un lead es relevante para esta industria."""
        pass
    
    def generate_custom_search_terms(self, base_keyword: str, city: str) -> List[str]:
        """Generar términos de búsqueda personalizados."""
        terms = [
            f"{base_keyword} {city}",
            f"{base_keyword} suppliers {city}",
            f"{base_keyword} distributors {city}",
            f"{base_keyword} companies {city}"
        ]
        return terms
    
    def get_serpapi_params(self, keyword: str, city: str) -> Dict:
        """Parámetros optimizados para SerpApi según la industria."""
        return {
            'q': f"{keyword} {city}",
            'location': city,
            'hl': 'es',
            'gl': 'es',
            'google_domain': 'google.es'
        }
    
    def get_linkedin_search_url(self, keyword: str, city: str) -> str:
        """URL optimizada para LinkedIn según la industria."""
        query = f"{keyword} {city}".replace(' ', '%20')
        return f"https://www.linkedin.com/search/results/companies/?keywords={query}"