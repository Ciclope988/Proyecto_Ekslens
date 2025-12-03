"""
EKSLENS - Medical Aesthetics Industry Configuration
Configuración especializada para medicina estética
"""

from typing import List, Dict
from .base_industry import BaseIndustry


class MedicalAestheticsIndustry(BaseIndustry):
    """Configuración especializada para medicina estética."""
    
    def get_industry_name(self) -> str:
        return "Medical Aesthetics"
    
    def get_default_keywords(self) -> List[str]:
        """Keywords específicas de medicina estética."""
        return [
            # Productos principales
            'botox', 'dermal fillers', 'hyaluronic acid',
            'restylane', 'juvederm', 'profhilo', 'gouri',
            
            # Tratamientos
            'aesthetic medicine', 'cosmetic treatments', 'anti aging',
            'facial aesthetics', 'injectable treatments',
            
            # Tipos de negocio
            'aesthetic clinic', 'cosmetic surgery', 'beauty clinic',
            'medical spa', 'dermatology clinic', 'plastic surgery'
        ]
    
    def get_search_terms(self) -> List[str]:
        """Términos de búsqueda optimizados para medicina estética."""
        return [
            'medical supplies', 'healthcare equipment', 'surgical instruments',
            'dental supplies', 'laboratory equipment', 'pharmaceutical supplies',
            'medical devices', 'hospital equipment', 'clinic supplies',
            'aesthetic supplies', 'dermal fillers', 'botox supplies',
            'medical aesthetics', 'cosmetic surgery supplies', 'beauty clinic equipment',
            'injection supplies', 'hyaluronic acid', 'aesthetic training'
        ]
    
    def get_search_filters(self) -> Dict:
        """Filtros específicos para medicina estética."""
        return {
            'company_sizes': [
                '%22B%22',  # Small (1-10 employees)
                '%22C%22',  # Medium (11-50 employees)  
                '%22D%22',  # Medium-Large (51-200 employees)
                '%22E%22',  # Large (201-500 employees)
            ],
            'sort_options': ['relevance', 'date', 'followerCount'],
            'excluded_terms': ['hospital', 'university', 'government', 'non-profit']
        }
    
    def get_company_indicators(self) -> List[str]:
        """Indicadores de empresas relevantes en medicina estética."""
        return [
            # Palabras clave en nombre/descripción
            'aesthetic', 'beauty', 'cosmetic', 'dermal', 'botox',
            'filler', 'clinic', 'medical spa', 'anti aging',
            'skin care', 'facial', 'injection', 'treatment',
            
            # Marcas conocidas
            'restylane', 'juvederm', 'sculptra', 'radiesse',
            'belotero', 'teosyal', 'profhilo', 'gouri',
            
            # Tipos de servicios
            'distributor', 'supplier', 'training', 'equipment'
        ]
    
    def validate_lead(self, lead_data: Dict) -> bool:
        """Validar si un lead es relevante para medicina estética."""
        name = lead_data.get('name', '').lower()
        description = lead_data.get('description', '').lower()
        url = lead_data.get('url', '').lower()
        
        # Texto combinado para análisis
        combined_text = f"{name} {description} {url}"
        
        # Indicadores positivos
        positive_indicators = self.get_company_indicators()
        positive_score = sum(1 for indicator in positive_indicators 
                           if indicator.lower() in combined_text)
        
        # Indicadores negativos (excluir)
        negative_indicators = [
            'hospital', 'university', 'school', 'government',
            'insurance', 'pharmacy chain', 'drugstore'
        ]
        negative_score = sum(1 for indicator in negative_indicators 
                           if indicator.lower() in combined_text)
        
        # Validación: más indicadores positivos que negativos
        return positive_score > negative_score and positive_score >= 1
    
    def get_serpapi_params(self, keyword: str, city: str) -> Dict:
        """Parámetros SerpApi optimizados para medicina estética."""
        base_params = super().get_serpapi_params(keyword, city)
        
        # Agregar filtros específicos
        base_params.update({
            'q': f'"{keyword}" "{city}" (clinic OR aesthetic OR beauty OR medical OR supplies OR distributor)',
            'num': 10,  # Más resultados para medicina estética
            'filter': 1  # Filtrar duplicados
        })
        
        return base_params
    
    def get_linkedin_search_url(self, keyword: str, city: str) -> str:
        """URL LinkedIn optimizada para medicina estética."""
        # Combinar keyword con términos específicos de medicina estética
        enhanced_query = f"{keyword} aesthetic medical {city}".replace(' ', '%20')
        base_url = "https://www.linkedin.com/search/results/companies/"
        
        # Agregar filtros de industria
        industry_filter = "&industryCompanyVertical=%5B%22147%22%5D"  # Health, Wellness & Fitness
        
        return f"{base_url}?keywords={enhanced_query}{industry_filter}"
    
    def generate_email_context(self, lead_data: Dict) -> Dict:
        """Generar contexto especializado para emails de medicina estética."""
        return {
            'industry': 'medicina estética',
            'products': ['fillers dérmicos', 'botox', 'ácido hialurónico'],
            'services': ['distribución', 'formación', 'soporte técnico'],
            'target_audience': 'clínicas estéticas y profesionales médicos',
            'value_proposition': 'productos premium con certificación médica',
            'tone': 'profesional pero accesible'
        }