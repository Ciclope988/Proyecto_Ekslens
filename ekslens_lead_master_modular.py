"""
EKSLENS - Lead Master Coordinator (Modular)
Coordinador principal usando arquitectura modular por industrias
"""

import os
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional
import json

# Imports del sistema modular
from env_config import load_config
from database import Database

# Imports de scrapers especializados
from scrapers.serpapi_scraper import SerpApiScraper
# LINKEDIN TEMPORALMENTE DESHABILITADO POR POLÍTICAS DE USO
# # LINKEDIN TEMPORALMENTE DESHABILITADO POR POLÍTICAS DE USO
# from scrapers.linkedin_scraper import LinkedInScraper

# Imports de configuraciones por industria
from industries.medical_aesthetics import MedicalAestheticsIndustry
from industries.real_estate import RealEstateIndustry

# Import para AI
try:
    import google.generativeai as genai
except ImportError:
    genai = None

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EkslensLeadMaster:
    """Coordinador principal con arquitectura modular."""
    
    def __init__(self, industry_type: str = 'medical_aesthetics'):
        """Inicializar el coordinador con una industria específica."""
        self.config = load_config()
        self.db = Database()
        
        # Configurar industria
        self.industry = self._setup_industry(industry_type)
        
        # Configurar APIs desde config
        self.serpapi_key = self.config.get('serpapi_key') or self.config.get('SERPAPI_KEY')
        self.google_api_key = self.config.get('GOOGLE_API_KEY') 
        self.linkedin_email = self.config.get('LINKEDIN_EMAIL')
        self.linkedin_password = self.config.get('LINKEDIN_PASSWORD')
        
        # Configurar AI
        if self.google_api_key and genai:
            genai.configure(api_key=self.google_api_key)
            self.ai_model = genai.GenerativeModel('gemini-pro')
        else:
            self.ai_model = None
        
        # Inicializar scrapers especializados
        self.serpapi_scraper = SerpApiScraper(self.serpapi_key, self.industry)
        
        # LINKEDIN TEMPORALMENTE DESHABILITADO POR POLÍTICAS DE USO
        # self.linkedin_scraper = LinkedInScraper(self.linkedin_email, self.linkedin_password, self.industry)
        self.linkedin_scraper = None
        
        # Estadísticas de sesión
        self.session_stats = {
            'searches_performed': 0,
            'leads_found': 0,
            'leads_saved': 0,
            'emails_generated': 0,
            'execution_time': 0,
            'industry': self.industry.name
        }
    
    def _setup_industry(self, industry_type: str):
        """Configurar industria específica."""
        industry_map = {
            'medical_aesthetics': MedicalAestheticsIndustry(),
            'real_estate': RealEstateIndustry()
        }
        
        industry = industry_map.get(industry_type)
        if not industry:
            logger.warning(f"Industria '{industry_type}' no encontrada, usando medical_aesthetics por defecto")
            industry = MedicalAestheticsIndustry()
        
        logger.info(f"✅ Industria configurada: {industry.name}")
        return industry
    
    def run_master_search_with_keywords(self, cities: List[str], keywords: List[str], max_searches: int = 3, use_serpapi: bool = True, use_linkedin: bool = True) -> Dict:
        """Ejecutar búsqueda completa con keywords personalizadas."""
        start_time = time.time()
        
        print("🚀 EKSLENS LEAD MASTER - ARQUITECTURA MODULAR")
        print("="*60)
        print(f"📋 Industria: {self.industry.name}")
        print(f"🎯 Keywords: {', '.join(keywords[:5])}{'...' if len(keywords) > 5 else ''}")
        print(f"🏙️ Ciudades: {', '.join(cities[:3])}{'...' if len(cities) > 3 else ''}")
        print(f"🔍 Búsquedas máximas: {max_searches}")
        print(f"📊 SerpApi: {'✅' if use_serpapi else '❌'}")
        print(f"🔗 LinkedIn: {'✅' if use_linkedin else '❌'}")
        print()
        
        results = {
            'serpapi_results': [],
            'linkedin_results': [],
            'ai_emails': [],
            'total_leads': 0,
            'execution_summary': {},
            'industry': self.industry.name
        }
        
        try:
            serpapi_leads = []
            linkedin_leads = []
            
            # FASE 1: SerpApi Search (condicional)
            if use_serpapi:
                print("🔍 FASE 1: BÚSQUEDA SERPAPI")
                print("="*40)
                serpapi_leads = self.serpapi_scraper.search_by_keywords(cities, keywords, max_searches)
                results['serpapi_results'] = serpapi_leads
                
                # Guardar leads SerpApi en BD
                for lead in serpapi_leads:
                    lead_id = self._save_lead_to_db(lead)
                    if lead_id:
                        lead['id'] = lead_id
                        self.session_stats['leads_saved'] += 1
                        
                print(f"   ✅ SerpApi: {len(serpapi_leads)} leads encontrados")
            else:
                print("⏭️ FASE 1: SERPAPI OMITIDA")
                print("="*40)
                results['serpapi_results'] = []

            # FASE 2: LinkedIn Search (TEMPORALMENTE DESHABILITADO)  
            print("\n🚫 FASE 2: LINKEDIN DESHABILITADO")
            print("="*40)
            print("   ⚠️ LinkedIn scraping temporalmente deshabilitado")
            print("   📧 Esperando respuesta sobre API oficial o políticas")
            print("   🔍 Usa SerpAPI como alternativa principal")
            results['linkedin_results'] = []
            
            # Código LinkedIn comentado por políticas de uso:
            # if use_linkedin:
            #     print("\n🔗 FASE 2: BÚSQUEDA LINKEDIN")
            #     print("="*40)
            #     linkedin_leads = self.linkedin_scraper.search_by_keywords(cities, keywords)
            #     results['linkedin_results'] = linkedin_leads
            #     
            #     # Guardar leads LinkedIn en BD
            #     for lead in linkedin_leads:
            #         lead_id = self._save_lead_to_db(lead)
            #         if lead_id:
            #             lead['id'] = lead_id
            #             
            #     print(f"   ✅ LinkedIn: {len(linkedin_leads)} leads encontrados")
            # else:
            #     print("\n⏭️ FASE 2: LINKEDIN OMITIDA")
            #     print("="*40)
            #     results['linkedin_results'] = []
            
            # FASE 3: AI Email Generation
            if self.ai_model:
                print("\n🤖 FASE 3: GENERACIÓN AI DE EMAILS")
                print("="*40)
                all_leads = serpapi_leads + linkedin_leads
                ai_emails = self._generate_ai_emails(all_leads[:5])  # Solo primeros 5
                results['ai_emails'] = ai_emails
                self.session_stats['emails_generated'] = len(ai_emails)
            
            # FASE 4: Resumen Final
            self.session_stats['execution_time'] = time.time() - start_time
            self.session_stats['leads_found'] = len(serpapi_leads) + len(linkedin_leads)
            
            results['total_leads'] = self.session_stats['leads_found']
            results['execution_summary'] = self.session_stats
            
            self._show_final_summary(results)
            
        except Exception as e:
            logger.error(f"❌ Error en búsqueda master: {e}")
            print(f"❌ Error en búsqueda master: {e}")
        
        return results
    
    def run_master_search(self, cities: List[str], max_searches: int = 3) -> Dict:
        """Ejecutar búsqueda con keywords por defecto de la industria."""
        default_keywords = self.industry.get_default_keywords()[:5]  # Usar primeras 5 keywords
        return self.run_master_search_with_keywords(cities, default_keywords, max_searches)
    
    def change_industry(self, industry_type: str):
        """Cambiar a una industria diferente."""
        old_industry = self.industry.name
        self.industry = self._setup_industry(industry_type)
        
        # Reinicializar scrapers con nueva industria
        self.serpapi_scraper = SerpApiScraper(self.serpapi_key, self.industry)
        self.linkedin_scraper = LinkedInScraper(self.linkedin_email, self.linkedin_password, self.industry)
        
        print(f"🔄 Industria cambiada: {old_industry} → {self.industry.name}")
    
    def _save_lead_to_db(self, lead_data: Dict) -> Optional[int]:
        """Guardar lead en base de datos."""
        try:
            # Debug: mostrar datos del lead
            name = lead_data.get('name', 'N/A')
            linkedin_url = lead_data.get('linkedin_url', 'N/A')
            print(f"   💾 Intentando guardar: {name} | {linkedin_url[:30]}...")
            
            # Verificar que tenga los campos mínimos requeridos
            if not lead_data.get('name') or not lead_data.get('linkedin_url'):
                print(f"   ❌ Lead incompleto - name: {bool(lead_data.get('name'))}, url: {bool(lead_data.get('linkedin_url'))}")
                return None
            
            # Verificar si ya existe este perfil en BD (buscar en ambos campos url y linkedin_url)
            linkedin_url = lead_data.get('linkedin_url', '')
            if linkedin_url:
                try:
                    existing_leads = self.db.get_latest_leads(50)  # Revisar últimos 50
                    for existing_lead in existing_leads:
                        existing_url = existing_lead.get('linkedin_url') or existing_lead.get('url', '')
                        if existing_url == linkedin_url:
                            print(f"   ⚠️ Lead duplicado encontrado: {lead_data['name']}")
                            return None
                except Exception as e:
                    print(f"   ⚠️ Error verificando duplicados: {e}")
                    pass  # Si hay error verificando duplicados, continuar
            
            # Intentar guardar
            print(f"   📝 Guardando en BD...")
            lead_id = self.db.save_lead(
                name=lead_data.get('name', ''),
                email='',  # Se llenará después
                phone='',
                url=lead_data.get('linkedin_url', ''),
                description=lead_data.get('description', ''),
                source=lead_data.get('source', ''),
                keyword=lead_data.get('keyword', lead_data.get('keyword_used', '')),
                industry=lead_data.get('industry', self.industry.name)
            )
            
            if lead_id:
                print(f"   ✅ Lead guardado exitosamente: {lead_data['name']} (ID: {lead_id})")
                self.session_stats['leads_saved'] += 1
                return lead_id
            else:
                print(f"   ❌ Error: save_lead retornó None para {lead_data['name']}")
                return None
                
        except Exception as e:
            print(f"   ❌ Excepción guardando lead: {e}")
            import traceback
            traceback.print_exc()
            return None
            return None
    
    def _generate_ai_emails(self, leads: List[Dict]) -> List[Dict]:
        """Generar emails personalizados con AI."""
        emails = []
        
        if not self.ai_model:
            print("⚠️ AI no disponible - falta Google API key")
            return emails
        
        for lead in leads:
            try:
                # Obtener contexto específico de la industria
                context = self.industry.generate_email_context(lead)
                
                # Crear prompt específico por industria
                prompt = self._create_industry_email_prompt(lead, context)
                
                # Generar email con AI
                response = self.ai_model.generate_content(prompt)
                
                email_data = {
                    'lead_name': lead.get('name'),
                    'lead_id': lead.get('id'),
                    'email_content': response.text,
                    'industry': self.industry.name,
                    'generated_date': datetime.now()
                }
                emails.append(email_data)
                
                print(f"   ✅ Email generado para: {lead.get('name', 'Sin nombre')[:40]}...")
                
            except Exception as e:
                logger.error(f"Error generando email para {lead.get('name', 'lead')}: {e}")
                continue
        
        return emails
    
    def _create_industry_email_prompt(self, lead: Dict, context: Dict) -> str:
        """Crear prompt específico por industria."""
        base_prompt = f"""
        Genera un email profesional y personalizado para contactar a la empresa "{lead.get('name', '')}" 
        del sector {context['industry']}.
        
        Contexto de la industria:
        - Productos principales: {', '.join(context['products'])}
        - Servicios: {', '.join(context['services'])}
        - Audiencia objetivo: {context['target_audience']}
        - Propuesta de valor: {context['value_proposition']}
        
        El email debe:
        1. Ser profesional pero accesible
        2. Mencionar productos específicos de {context['industry']}
        3. Ofrecer valor inmediato
        4. Incluir un call-to-action claro
        5. Ser personalizado para "{lead.get('name', '')}"
        
        Longitud: Máximo 150 palabras.
        Tono: {context['tone']}
        """
        return base_prompt
    
    def _show_final_summary(self, results: Dict):
        """Mostrar resumen final de la ejecución."""
        print("\n" + "="*60)
        print("📊 RESUMEN FINAL - EKSLENS MODULAR")
        print("="*60)
        print(f"🏭 Industria: {self.industry.name}")
        print(f"📊 Total Leads: {results['total_leads']}")
        print(f"🔍 SerpApi: {len(results['serpapi_results'])} leads")
        print(f"🔗 LinkedIn: {len(results['linkedin_results'])} leads")
        print(f"🤖 Emails AI: {len(results['ai_emails'])} generados")
        print(f"💾 Leads guardados: {self.session_stats['leads_saved']}")
        print(f"⏱️ Tiempo total: {self.session_stats['execution_time']:.1f}s")
        
        if self.session_stats['execution_time'] > 0:
            efficiency = results['total_leads'] / (self.session_stats['execution_time'] / 60)
            print(f"💡 Eficiencia: {efficiency:.1f} leads/min")
        
        print(f"\n✅ EKSLENS MODULAR COMPLETADO")
    
    def get_available_industries(self) -> List[str]:
        """Obtener lista de industrias disponibles."""
        return ['medical_aesthetics', 'real_estate']
    
    def get_industry_info(self) -> Dict:
        """Obtener información de la industria actual."""
        return {
            'name': self.industry.name,
            'keywords': self.industry.get_default_keywords(),
            'search_terms': self.industry.get_search_terms()[:5],
            'company_indicators': self.industry.get_company_indicators()[:5]
        }


def main():
    """Función principal del coordinador modular."""
    print("🚀 EKSLENS LEAD MASTER - ARQUITECTURA MODULAR")
    print("="*60)
    print("🎯 Sistema modular por industrias")
    print("📋 Industrias disponibles:")
    print("   1. Medical Aesthetics (medicina estética)")
    print("   2. Real Estate (inmobiliaria)")
    print()
    
    # Seleccionar industria
    industry_choice = input("Selecciona industria [1-medical_aesthetics, 2-real_estate]: ").strip()
    
    if industry_choice == '2':
        industry_type = 'real_estate'
    else:
        industry_type = 'medical_aesthetics'
    
    # Crear coordinador con industria seleccionada
    master = EkslensLeadMaster(industry_type)
    
    print(f"\n✅ Coordinador inicializado para: {master.industry.name}")
    print(f"🎯 Keywords por defecto: {', '.join(master.industry.get_default_keywords()[:5])}...")
    
    # Configurar búsqueda
    cities_input = input("\nCiudades objetivo (separadas por coma) [Madrid,Barcelona,Valencia]: ").strip()
    if cities_input:
        cities = [city.strip().lower() for city in cities_input.split(',')]
    else:
        cities = ["madrid", "barcelona", "valencia"]
    
    keywords_input = input("Keywords personalizadas (separadas por coma) [usar por defecto]: ").strip()
    if keywords_input:
        keywords = [kw.strip() for kw in keywords_input.split(',')]
    else:
        keywords = master.industry.get_default_keywords()[:3]
    
    max_searches = input("Número máximo de búsquedas SerpApi [2]: ").strip()
    try:
        max_searches = int(max_searches) if max_searches else 2
    except:
        max_searches = 2
    
    input(f"\n🚀 Presiona ENTER para iniciar búsqueda en {master.industry.name}...")
    
    # Ejecutar búsqueda
    results = master.run_master_search_with_keywords(cities, keywords, max_searches)
    
    # Guardar log
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    log_file = f"ekslens_modular_{industry_type}_{timestamp}.json"
    
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n📄 Log guardado en: {log_file}")
    print("📊 Revisa los leads en la base de datos para continuar")


if __name__ == "__main__":
    main()