"""
EKSLENS - Database Queries
Operaciones de consulta e inserción de datos
"""

import logging
from typing import Optional, List, Dict
from backend.database.connection import DatabaseConnection
from backend.database.models import DatabaseModels

logger = logging.getLogger(__name__)


class DatabaseQueries:
    """Clase para operaciones de base de datos."""
    
    def __init__(self):
        """Inicializar conexión a base de datos."""
        self.db_conn = DatabaseConnection()
        self.models = DatabaseModels()
    
    def create_tables(self) -> bool:
        """Crear tablas necesarias para Ekslens."""
        try:
            logger.info("🏗️ Creando tablas de Ekslens...")
            
            # Crear tablas principales
            tables = [
                self.models.get_leads_table_schema(),
                self.models.get_emails_table_schema(),
                self.models.get_search_sessions_table_schema()
            ]
            
            for i, table_sql in enumerate(tables, 1):
                result = self.db_conn.execute_query(table_sql)
                if result is not None:
                    table_name = ["leads", "generated_emails", "search_sessions"][i-1]
                    logger.info(f"✅ Tabla {table_name} creada/verificada")
                else:
                    logger.error(f"❌ Error creando tabla {i}")
                    return False
            
            # Crear índices
            logger.info("🔍 Creando índices...")
            for index_sql in self.models.get_indexes():
                self.db_conn.execute_query(index_sql)
            
            # Aplicar migraciones
            self.migrate_table_if_needed()
            
            logger.info("✅ Todas las tablas e índices creados correctamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creando tablas: {e}")
            return False
    
    def migrate_table_if_needed(self) -> bool:
        """Migrar tabla existente agregando nuevas columnas."""
        try:
            logger.info("🔄 Verificando migraciones necesarias...")
            
            for migration in self.models.get_migrations():
                result = self.db_conn.execute_query(migration)
                if result is not None:
                    logger.info("✅ Migración aplicada")
                else:
                    logger.warning("⚠️ Error en migración (posiblemente ya aplicada)")
            
            logger.info("✅ Migraciones completadas")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error aplicando migraciones: {e}")
            return False
    
    def check_duplicate_lead(self, nombre: str, website: str = None) -> Optional[int]:
        """
        Verificar si ya existe un lead con el mismo nombre o website.
        
        Args:
            nombre: Nombre del lead
            website: Website del lead (opcional)
            
        Returns:
            ID del lead existente o None si no existe
        """
        try:
            query = "SELECT id FROM leads WHERE nombre = %s"
            params = (nombre,)
            
            if website and website.strip():
                query += " OR website = %s"
                params = (nombre, website)
            
            result = self.db_conn.execute_query(query, params)
            
            if result and len(result) > 0:
                return result[0]['id']
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error verificando duplicados: {e}")
            return None
    
    def insert_lead(self, lead_data: Dict) -> Optional[int]:
        """
        Insertar un nuevo lead verificando duplicados.
        
        Args:
            lead_data: Diccionario con datos del lead
            
        Returns:
            ID del lead insertado o existente
        """
        try:
            # Mapear 'name' a 'nombre' si existe
            if 'name' in lead_data:
                lead_data['nombre'] = lead_data.pop('name')
            
            # Verificar campos obligatorios
            if not lead_data.get('nombre'):
                logger.error("❌ Campo 'nombre' es obligatorio")
                return None
            
            # Verificar duplicados
            nombre = lead_data['nombre']
            website = lead_data.get('website', '')
            
            existing_id = self.check_duplicate_lead(nombre, website)
            if existing_id:
                logger.info(f"ℹ️ Lead '{nombre}' ya existe con ID: {existing_id}")
                return existing_id
            
            # Construir query dinámicamente
            columns = list(lead_data.keys())
            placeholders = [f"%({col})s" for col in columns]
            
            query = f"""
            INSERT INTO leads ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
            RETURNING id
            """
            
            result = self.db_conn.execute_query(query, lead_data)
            
            if result and len(result) > 0:
                lead_id = result[0]['id']
                logger.info(f"✅ Lead insertado con ID: {lead_id}")
                return lead_id
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error insertando lead: {e}")
            return None
    
    def insert_email(self, email_data: Dict) -> Optional[int]:
        """
        Insertar email generado.
        
        Args:
            email_data: Diccionario con datos del email
            
        Returns:
            ID del email insertado o None si error
        """
        try:
            if not email_data.get('lead_id') or not email_data.get('content'):
                logger.error("❌ Campos 'lead_id' y 'content' son obligatorios")
                return None
            
            columns = list(email_data.keys())
            placeholders = [f"%({col})s" for col in columns]
            
            query = f"""
            INSERT INTO generated_emails ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
            RETURNING id
            """
            
            result = self.db_conn.execute_query(query, email_data)
            
            if result and len(result) > 0:
                email_id = result[0]['id']
                logger.info(f"✅ Email insertado con ID: {email_id}")
                return email_id
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error insertando email: {e}")
            return None
    
    def get_leads(self, limit: int = 100, status: str = None) -> List[Dict]:
        """
        Obtener leads de la base de datos.
        
        Args:
            limit: Número máximo de leads
            status: Filtrar por status específico
            
        Returns:
            Lista de leads
        """
        try:
            query = "SELECT * FROM leads"
            params = None
            
            if status:
                query += " WHERE status = %s"
                params = (status,)
            
            query += f" ORDER BY found_date DESC LIMIT {limit}"
            
            results = self.db_conn.execute_query(query, params)
            return results if results else []
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo leads: {e}")
            return []
    
    def get_lead_emails(self, lead_id: int) -> List[Dict]:
        """Obtener emails de un lead específico."""
        try:
            query = """
            SELECT * FROM generated_emails 
            WHERE lead_id = %s 
            ORDER BY generated_date DESC
            """
            
            results = self.db_conn.execute_query(query, (lead_id,))
            return results if results else []
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo emails del lead {lead_id}: {e}")
            return []
    
    def update_linkedin_invite_status(self, lead_id: int, status: str = 'sent') -> bool:
        """Marcar invitación LinkedIn como enviada."""
        try:
            query = """
            UPDATE leads 
            SET linkedin_invite_sent = true,
                linkedin_invite_date = CURRENT_TIMESTAMP,
                linkedin_invite_status = %s
            WHERE id = %s
            """
            
            result = self.db_conn.execute_query(query, (status, lead_id))
            return result is not None
            
        except Exception as e:
            logger.error(f"❌ Error actualizando status LinkedIn lead {lead_id}: {e}")
            return False
    
    def update_instagram_invite_status(self, lead_id: int, status: str = 'sent') -> bool:
        """Marcar invitación Instagram como enviada."""
        try:
            query = """
            UPDATE leads 
            SET instagram_invite_sent = true,
                instagram_invite_date = CURRENT_TIMESTAMP,
                instagram_invite_status = %s
            WHERE id = %s
            """
            
            result = self.db_conn.execute_query(query, (status, lead_id))
            return result is not None
            
        except Exception as e:
            logger.error(f"❌ Error actualizando status Instagram lead {lead_id}: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Obtener estadísticas de la base de datos."""
        try:
            stats = {}
            
            # Total leads
            result = self.db_conn.execute_query("SELECT COUNT(*) as total FROM leads")
            stats['total_leads'] = result[0]['total'] if result else 0
            
            # Leads por fuente
            result = self.db_conn.execute_query("""
                SELECT COALESCE(source, 'Sin fuente') as source, COUNT(*) as count 
                FROM leads 
                GROUP BY source
            """)
            stats['leads_by_source'] = {
                row['source']: row['count'] 
                for row in result if result
            } if result else {}
            
            # Leads por status
            result = self.db_conn.execute_query("""
                SELECT COALESCE(status, 'Sin estado') as status, COUNT(*) as count 
                FROM leads 
                GROUP BY status
            """)
            stats['leads_by_status'] = {
                row['status']: row['count'] 
                for row in result if result
            } if result else {}
            
            # Total emails
            result = self.db_conn.execute_query("SELECT COUNT(*) as total FROM generated_emails")
            stats['total_emails'] = result[0]['total'] if result else 0
            
            # Invitaciones LinkedIn
            result = self.db_conn.execute_query("SELECT COUNT(*) as total FROM leads WHERE linkedin_invite_sent = true")
            stats['linkedin_invites_sent'] = result[0]['total'] if result else 0
            
            # Invitaciones Instagram
            result = self.db_conn.execute_query("SELECT COUNT(*) as total FROM leads WHERE instagram_invite_sent = true")
            stats['instagram_invites_sent'] = result[0]['total'] if result else 0
            
            # Emails por status
            result = self.db_conn.execute_query("""
                SELECT COALESCE(status, 'Sin estado') as status, COUNT(*) as count 
                FROM generated_emails 
                GROUP BY status
            """)
            stats['emails_by_status'] = {
                row['status']: row['count'] 
                for row in result if result
            } if result else {}
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas: {e}")
            return {}
    
    def search_leads_by_keyword(self, keyword: str) -> List[Dict]:
        """Buscar leads que contengan una keyword específica."""
        try:
            query = """
            SELECT * FROM leads 
            WHERE 
                LOWER(nombre) LIKE %s OR
                LOWER(description) LIKE %s OR
                LOWER(website) LIKE %s OR
                LOWER(source) LIKE %s
            ORDER BY found_date DESC
            LIMIT 20
            """
            
            keyword_pattern = f"%{keyword.lower()}%"
            params = (keyword_pattern, keyword_pattern, keyword_pattern, keyword_pattern)
            
            results = self.db_conn.execute_query(query, params)
            return results if results else []
            
        except Exception as e:
            logger.error(f"Error buscando leads por keyword '{keyword}': {e}")
            return []
    
    def count_leads(self) -> int:
        """Contar total de leads en la base de datos."""
        try:
            result = self.db_conn.execute_query("SELECT COUNT(*) as count FROM leads")
            return result[0]['count'] if result else 0
        except Exception as e:
            logger.error(f"Error contando leads: {e}")
            return 0
    
    def get_latest_leads(self, limit: int = 10) -> List[Dict]:
        """Obtener los últimos leads guardados."""
        try:
            query = """
                SELECT id, nombre as name, email, phone, 
                       COALESCE(linkedin_url, website) as url, website, linkedin_url,
                       description, search_term as keyword, source, 
                       created_at, location
                FROM leads 
                ORDER BY created_at DESC 
                LIMIT %s
            """
            
            results = self.db_conn.execute_query(query, (limit,))
            return results if results else []
            
        except Exception as e:
            logger.error(f"Error obteniendo últimos leads: {e}")
            return []
    
    def save_manual_linkedin_lead(self, nombre: str, email: str = '', telefono: str = '', 
                                linkedin_url: str = '', description: str = '', 
                                industria: str = 'medical_aesthetics') -> Optional[int]:
        """
        Guardar lead de LinkedIn agregado manualmente.
        """
        try:
            # Validar datos básicos
            if not nombre.strip():
                logger.error("Error: El nombre es obligatorio")
                return None
            
            # Preparar datos del lead manual
            lead_data = {
                'nombre': nombre.strip(),
                'email': email.strip() if email else '',
                'phone': telefono.strip() if telefono else '',
                'linkedin_url': linkedin_url.strip() if linkedin_url else '',
                'description': description.strip() if description else 'Lead agregado manualmente',
                'source': 'LinkedIn (Manual)',
                'status': 'pending',
                'extraction_method': 'manual_entry'
            }
            
            # Limpiar campos vacíos
            clean_data = {k: v for k, v in lead_data.items() if k in ['nombre', 'source', 'status', 'extraction_method'] or v}
            
            lead_id = self.insert_lead(clean_data)
            
            if lead_id:
                logger.info(f"✅ Lead manual de LinkedIn guardado: {nombre} (ID: {lead_id})")
                print(f"✅ Lead manual agregado exitosamente: {nombre}")
                return lead_id
            else:
                logger.error(f"❌ Error al guardar lead manual: {nombre}")
                return None
                
        except Exception as e:
            logger.error(f"Error guardando lead manual de LinkedIn: {e}")
            print(f"❌ Error al guardar lead manual: {e}")
            return None
    
    def close(self):
        """Cerrar conexión a la base de datos."""
        self.db_conn.close()
