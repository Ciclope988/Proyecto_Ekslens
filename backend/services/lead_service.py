"""
EKSLENS - Lead Service
Servicio de gestión de leads
"""

import logging
from typing import Dict, Optional, List
from backend.database.queries import DatabaseQueries

logger = logging.getLogger(__name__)


class LeadService:
    """Servicio para operaciones con leads."""
    
    def __init__(self):
        """Inicializar servicio de leads."""
        self.db = DatabaseQueries()
    
    def get_database_stats(self) -> Dict:
        """Obtener estadísticas de la base de datos con leads recientes."""
        try:
            if not self.db.db_conn.connected:
                return {'error': 'No se pudo conectar a la base de datos'}
            
            stats = self.db.get_stats()
            recent_leads = self.db.get_leads(limit=10)
            
            formatted_stats = {
                'total_leads': stats.get('total_leads', 0),
                'total_emails': stats.get('total_emails', 0),
                'leads_by_source': stats.get('leads_by_source', {}),
                'leads_by_status': stats.get('leads_by_status', {}),
                'recent_leads': self._format_leads(recent_leads)
            }
            
            return formatted_stats
            
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {'error': str(e)}
    
    def _format_leads(self, leads: List[Dict]) -> List[Dict]:
        """Formatear leads para la respuesta."""
        formatted = []
        
        for lead in leads:
            # Manejar fechas de forma segura
            found_date = lead.get('found_date')
            if found_date and hasattr(found_date, 'strftime'):
                date_str = found_date.strftime('%Y-%m-%d %H:%M')
            elif found_date:
                date_str = str(found_date)
            else:
                date_str = 'No disponible'
            
            formatted_lead = {
                'id': lead.get('id'),
                'name': lead.get('nombre', 'Sin nombre'),
                'source': lead.get('source', 'Desconocido'),
                'status': lead.get('status', 'pending'),
                'found_date': date_str,
                'linkedin_url': lead.get('linkedin_url', ''),
                'website': lead.get('website', ''),
                'email': lead.get('email', ''),
                'phone': lead.get('phone', '')
            }
            formatted.append(formatted_lead)
        
        return formatted
    
    def add_manual_lead(self, data: Dict) -> Dict:
        """Agregar lead de LinkedIn manualmente."""
        try:
            if not data:
                return {'error': 'No se recibieron datos'}
            
            # Validar datos requeridos
            nombre = data.get('nombre', '').strip()
            if not nombre:
                return {'error': 'El nombre es obligatorio'}
            
            # Obtener datos opcionales
            email = data.get('email', '').strip()
            telefono = data.get('telefono', '').strip()
            linkedin_url = data.get('linkedin_url', '').strip()
            description = data.get('description', '').strip()
            industria = data.get('industria', 'medical_aesthetics')
            
            # Guardar en base de datos
            if not self.db.db_conn.connected:
                return {'error': 'No se pudo conectar a la base de datos'}
            
            lead_id = self.db.save_manual_linkedin_lead(
                nombre=nombre,
                email=email, 
                telefono=telefono,
                linkedin_url=linkedin_url,
                description=description,
                industria=industria
            )
            
            if lead_id:
                return {
                    'success': True,
                    'message': f'Lead "{nombre}" agregado exitosamente',
                    'lead_id': lead_id
                }
            else:
                return {'error': 'Error al guardar el lead en la base de datos'}
                
        except Exception as e:
            logger.error(f"Error adding manual lead: {e}")
            return {'error': f'Error interno: {str(e)}'}
    
    def execute_custom_query(self, query: str) -> Dict:
        """Ejecutar consulta SQL personalizada (solo SELECT por seguridad)."""
        try:
            if not query:
                return {'error': 'No se proporcionó consulta SQL'}
            
            query = query.strip()
            
            # Validación de seguridad: solo permitir SELECT
            if not query.upper().startswith('SELECT'):
                return {'error': 'Solo se permiten consultas SELECT por seguridad'}
            
            # Verificar comandos peligrosos
            dangerous_keywords = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 'CREATE', 'TRUNCATE', 'GRANT', 'REVOKE']
            query_upper = query.upper()
            
            for keyword in dangerous_keywords:
                if keyword in query_upper:
                    return {'error': f'Comando {keyword} no permitido por seguridad'}
            
            # Ejecutar consulta
            if not self.db.db_conn.connected:
                return {'error': 'No se pudo conectar a la base de datos'}
            
            results = self.db.db_conn.execute_query(query)
            
            if results:
                columns = list(results[0].keys()) if results else []
                return {
                    'success': True,
                    'results': results,
                    'columns': columns,
                    'count': len(results)
                }
            else:
                return {
                    'success': True,
                    'results': [],
                    'columns': [],
                    'count': 0
                }
                
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return {'error': f'Error en consulta: {str(e)}'}
    
    def close(self):
        """Cerrar conexión a base de datos."""
        self.db.close()
