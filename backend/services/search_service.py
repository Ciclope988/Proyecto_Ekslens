"""
EKSLENS - Search Service
Servicio de gestión de búsquedas de leads
"""

import logging
import threading
import json
from typing import Dict, List
from datetime import datetime
from backend.database.queries import DatabaseQueries
from ekslens_lead_master_modular import EkslensLeadMaster

logger = logging.getLogger(__name__)


class WebLogger:
    """Logger personalizado para capturar logs para la web."""
    
    def __init__(self):
        self.logs = []
        
    def add_log(self, level: str, message: str):
        """Añadir log con timestamp."""
        log_entry = {
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'level': level,
            'message': message
        }
        self.logs.append(log_entry)
        
        # Mantener solo los últimos 100 logs
        if len(self.logs) > 100:
            self.logs = self.logs[-100:]
    
    def get_logs(self) -> List[Dict]:
        """Obtener todos los logs."""
        return self.logs
    
    def clear_logs(self):
        """Limpiar logs."""
        self.logs = []


class SearchService:
    """Servicio para operaciones de búsqueda de leads."""
    
    def __init__(self):
        """Inicializar servicio de búsqueda."""
        self.db = DatabaseQueries()
        self.web_logger = WebLogger()
        
        # Estado de la aplicación
        self.app_state = {
            'is_running': False,
            'current_session': None,
            'last_results': None,
            'progress': 0,
            'status_message': 'Sistema listo'
        }
    
    def get_system_status(self) -> Dict:
        """Obtener estado actual del sistema."""
        try:
            # Verificar conexión a base de datos
            db_connected = self.db.db_conn.test_connection() if self.db.db_conn.connected else False
            
            stats = {}
            if db_connected:
                stats = self.db.get_stats()
            
            # Plan mensual SerpApi (placeholder)
            monthly_plan = {'searches_remaining': 100, 'recommended_daily': 3}
            
            return {
                'is_running': self.app_state['is_running'],
                'progress': self.app_state['progress'],
                'status_message': self.app_state['status_message'],
                'database_connected': db_connected,
                'total_leads': stats.get('total_leads', 0),
                'total_emails': stats.get('total_emails', 0),
                'linkedin_invites_sent': stats.get('linkedin_invites_sent', 0),
                'instagram_invites_sent': stats.get('instagram_invites_sent', 0),
                'serpapi_remaining': monthly_plan.get('searches_remaining', 100),
                'recommended_daily': monthly_plan.get('recommended_daily', 3)
            }
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {'error': str(e)}
    
    def start_search(self, data: Dict) -> Dict:
        """Iniciar búsqueda de leads."""
        if self.app_state['is_running']:
            return {'error': 'Ya hay una búsqueda en progreso'}
        
        try:
            cities = data.get('cities', ['madrid', 'barcelona', 'valencia'])
            keywords = data.get('keywords', ['botox', 'dermal fillers', 'aesthetic supplies'])
            max_searches = int(data.get('max_searches', 3))
            use_serpapi = data.get('use_serpapi', True)
            use_linkedin = data.get('use_linkedin', True)
            use_instagram = data.get('use_instagram', False)
            
            # Validaciones
            if max_searches > 10:
                return {'error': 'Máximo 10 búsquedas permitidas'}
            
            if len(cities) > 5:
                return {'error': 'Máximo 5 ciudades permitidas'}
            
            if len(keywords) > 10:
                return {'error': 'Máximo 10 palabras clave permitidas'}
            
            # Iniciar búsqueda en hilo separado
            search_thread = threading.Thread(
                target=self._run_search_process,
                args=(cities, keywords, max_searches, use_serpapi, use_linkedin, use_instagram)
            )
            search_thread.start()
            
            self.app_state['is_running'] = True
            self.app_state['progress'] = 0
            self.app_state['status_message'] = 'Iniciando búsqueda...'
            self.web_logger.clear_logs()
            self.web_logger.add_log('INFO', f'Búsqueda iniciada: {len(cities)} ciudades, {len(keywords)} keywords')
            
            return {'message': 'Búsqueda iniciada correctamente'}
            
        except Exception as e:
            logger.error(f"Error starting search: {e}")
            return {'error': str(e)}
    
    def _run_search_process(self, cities: List[str], keywords: List[str], max_searches: int, 
                           use_serpapi: bool, use_linkedin: bool, use_instagram: bool):
        """Ejecutar proceso de búsqueda en segundo plano."""
        try:
            self.web_logger.add_log('INFO', '🚀 Iniciando EKSLENS Lead Master')
            self.app_state['status_message'] = 'Configurando sistema...'
            self.app_state['progress'] = 10
            
            # Crear instancia del Lead Master
            master = EkslensLeadMaster('medical_aesthetics')
            
            # Configurar búsqueda
            self.web_logger.add_log('INFO', f'📍 Ciudades: {", ".join(cities)}')
            self.web_logger.add_log('INFO', f'🔍 Keywords: {", ".join(keywords)}')
            self.web_logger.add_log('INFO', f'🔍 SerpApi: {"✅" if use_serpapi else "❌"}')
            
            self.app_state['progress'] = 20
            self.app_state['status_message'] = 'Ejecutando búsquedas...'
            
            # Ejecutar búsqueda
            results = master.run_master_search_with_keywords(
                cities=cities, 
                keywords=keywords,
                max_searches=max_searches,
                use_serpapi=use_serpapi,
                use_linkedin=use_linkedin
            )
            
            self.app_state['progress'] = 90
            self.app_state['status_message'] = 'Finalizando...'
            
            # Guardar resultados
            self.app_state['last_results'] = results
            self.app_state['progress'] = 100
            self.app_state['status_message'] = f'✅ Completado: {results.get("total_leads", 0)} leads encontrados'
            
            self.web_logger.add_log('SUCCESS', f'🎯 Búsqueda completada exitosamente')
            self.web_logger.add_log('INFO', f'📊 Total leads: {results.get("total_leads", 0)}')
            
            # Guardar log de sesión
            timestamp = datetime.now().strftime('%Y%m%d_%H%M')
            log_file = f'web_session_{timestamp}.json'
            
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2, default=str)
            
            self.web_logger.add_log('INFO', f'📄 Log guardado: {log_file}')
            
        except Exception as e:
            error_msg = f'❌ Error en búsqueda: {str(e)}'
            self.web_logger.add_log('ERROR', error_msg)
            self.app_state['status_message'] = error_msg
            self.app_state['progress'] = 0
        
        finally:
            self.app_state['is_running'] = False
    
    def stop_search(self) -> Dict:
        """Detener búsqueda actual."""
        self.app_state['is_running'] = False
        self.app_state['status_message'] = 'Búsqueda detenida por el usuario'
        self.web_logger.add_log('WARNING', 'Búsqueda detenida por el usuario')
        return {'message': 'Búsqueda detenida'}
    
    def get_latest_results(self) -> Dict:
        """Obtener resultados de la última búsqueda."""
        if not self.app_state['last_results']:
            return None
        
        results = self.app_state['last_results']
        
        # Formatear resultados
        formatted_results = {
            'total_leads': results.get('total_leads', 0),
            'serpapi_leads': len(results.get('serpapi_results', [])),
            'linkedin_leads': len(results.get('linkedin_results', [])),
            'ai_emails': len(results.get('ai_emails', [])),
            'execution_summary': results.get('execution_summary', {}),
            'sample_leads': []
        }
        
        # Muestra de leads (primeros 5)
        all_leads = results.get('serpapi_results', []) + results.get('linkedin_results', [])
        for lead in all_leads[:5]:
            formatted_lead = {
                'name': lead.get('nombre', 'Sin nombre'),
                'source': lead.get('source', 'Desconocido'),
                'website': lead.get('website', ''),
                'description': lead.get('description', '')[:100] + '...' if len(lead.get('description', '')) > 100 else lead.get('description', '')
            }
            formatted_results['sample_leads'].append(formatted_lead)
        
        return formatted_results
    
    def get_logs(self) -> Dict:
        """Obtener logs en tiempo real."""
        return {
            'logs': self.web_logger.get_logs(),
            'is_running': self.app_state['is_running'],
            'progress': self.app_state['progress'],
            'status_message': self.app_state['status_message']
        }
    
    def get_available_industries(self) -> Dict:
        """Obtener industrias disponibles."""
        try:
            master = EkslensLeadMaster()
            industries = master.get_available_industries()
            
            return {
                'industries': industries,
                'current': master.industry.name if hasattr(master, 'industry') else 'medical_aesthetics'
            }
        except Exception as e:
            logger.error(f"Error getting industries: {e}")
            return {'error': str(e)}
    
    def change_industry(self, industry_type: str) -> Dict:
        """Cambiar industria activa."""
        try:
            if not industry_type:
                return {'error': 'industry_type requerido'}
            
            # Crear nueva instancia con industria específica
            master = EkslensLeadMaster(industry_type)
            info = master.get_industry_info()
            
            self.web_logger.add_log('INFO', f'🔄 Industria cambiada a: {info["name"]}')
            
            return {
                'message': f'Industria cambiada a {info["name"]}',
                'industry_info': info
            }
            
        except Exception as e:
            self.web_logger.add_log('ERROR', f'Error cambiando industria: {e}')
            return {'error': str(e)}
    
    def get_industry_info(self) -> Dict:
        """Obtener información de la industria actual."""
        try:
            master = EkslensLeadMaster()
            info = master.get_industry_info()
            return info
        except Exception as e:
            logger.error(f"Error getting industry info: {e}")
            return {'error': str(e)}
