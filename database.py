"""
EKSLENS - Database Connection
Conexión y gestión de PostgreSQL con pgAdmin
"""

import os
import psycopg2
import psycopg2.extras
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
import json
from env_config import load_config

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        """Inicializar conexión a PostgreSQL."""
        self.config = load_config()
        
        # Configuración de conexión
        self.host = self.config.get('DATABASE_HOST', 'localhost')
        self.port = int(self.config.get('DATABASE_PORT', 5433))
        self.database = self.config.get('DATABASE_NAME', 'ekslens_leads')
        self.user = self.config.get('DATABASE_USER', 'postgres')
        self.password = self.config.get('DATABASE_PASSWORD', 'Miat1005')
        
        self.connection = None
        self.connected = False
        
        # Intentar conexión inicial
        self.connect()
    
    def connect(self) -> bool:
        """Establecer conexión con PostgreSQL."""
        try:
            logger.info(f"🔌 Conectando a PostgreSQL: {self.host}:{self.port}/{self.database}")
            
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            
            # Configurar cursor para devolver diccionarios
            self.connection.autocommit = True
            
            self.connected = True
            logger.info("✅ Conexión PostgreSQL establecida")
            return True
            
        except psycopg2.Error as e:
            logger.error(f"❌ Error conectando a PostgreSQL: {e}")
            self.connected = False
            return False
        except Exception as e:
            logger.error(f"❌ Error inesperado en conexión: {e}")
            self.connected = False
            return False
    
    def execute_query(self, query: str, params: tuple = None) -> Optional[List[Dict]]:
        """
        Ejecutar consulta SQL y devolver resultados.
        
        Args:
            query: Consulta SQL
            params: Parámetros para la consulta
            
        Returns:
            Lista de diccionarios con los resultados
        """
        if not self.connected:
            if not self.connect():
                return None
        
        try:
            with self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                # Logging de la consulta para debugging (solo primeros 200 chars)
                query_preview = query[:200] + "..." if len(query) > 200 else query
                logger.info(f"🔍 Ejecutando consulta: {query_preview}")
                
                cursor.execute(query, params)
                
                # Si es SELECT, devolver resultados
                if query.strip().upper().startswith('SELECT') or 'RETURNING' in query.upper():
                    results = cursor.fetchall()
                    logger.info(f"✅ Consulta devolvió {len(results)} resultados")
                    return [dict(row) for row in results]
                
                # Para INSERT/UPDATE/DELETE sin RETURNING
                affected_rows = cursor.rowcount
                logger.info(f"✅ Consulta afectó {affected_rows} filas")
                return [{"affected_rows": affected_rows}]
                
        except psycopg2.Error as e:
            logger.error(f"❌ Error PostgreSQL ejecutando consulta: {e}")
            logger.error(f"🔍 Query: {query}")
            logger.error(f"🔍 Params: {params}")
            # Re-lanzar la excepción para que el endpoint web pueda capturarla
            raise e
        except Exception as e:
            logger.error(f"❌ Error inesperado: {e}")
            # Re-lanzar la excepción para que el endpoint web pueda capturarla
            raise e
    
    def create_tables(self) -> bool:
        """Crear tablas necesarias para Ekslens."""
        try:
            logger.info("🏗️ Creando tablas de Ekslens...")
            
            # Tabla principal de leads
            leads_table = """
            CREATE TABLE IF NOT EXISTS leads (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(255) NOT NULL,
                website VARCHAR(500),
                linkedin_url VARCHAR(500),
                instagram_url VARCHAR(500),
                instagram_username VARCHAR(100),
                phone VARCHAR(50),
                email VARCHAR(255),
                description TEXT,
                location VARCHAR(255),
                source VARCHAR(100),
                search_term VARCHAR(255),
                extraction_method VARCHAR(100),
                employee_count VARCHAR(50),
                followers_count VARCHAR(50),
                verified BOOLEAN DEFAULT FALSE,
                status VARCHAR(50) DEFAULT 'pending',
                found_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_contacted TIMESTAMP,
                linkedin_invite_sent BOOLEAN DEFAULT FALSE,
                linkedin_invite_date TIMESTAMP,
                linkedin_invite_status VARCHAR(50),
                instagram_invite_sent BOOLEAN DEFAULT FALSE,
                instagram_invite_date TIMESTAMP,
                instagram_invite_status VARCHAR(50),
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            
            # Tabla de emails generados
            emails_table = """
            CREATE TABLE IF NOT EXISTS generated_emails (
                id SERIAL PRIMARY KEY,
                lead_id INTEGER REFERENCES leads(id) ON DELETE CASCADE,
                subject VARCHAR(500),
                content TEXT NOT NULL,
                language VARCHAR(10) DEFAULT 'es',
                generated_by VARCHAR(100) DEFAULT 'Google Gemini',
                generated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sent_date TIMESTAMP,
                status VARCHAR(50) DEFAULT 'draft',
                response_received BOOLEAN DEFAULT FALSE,
                response_date TIMESTAMP,
                response_content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            
            # Tabla de sesiones de búsqueda
            search_sessions_table = """
            CREATE TABLE IF NOT EXISTS search_sessions (
                id SERIAL PRIMARY KEY,
                session_type VARCHAR(100),
                cities_searched TEXT,
                leads_found INTEGER DEFAULT 0,
                emails_generated INTEGER DEFAULT 0,
                serpapi_searches_used INTEGER DEFAULT 0,
                linkedin_companies_found INTEGER DEFAULT 0,
                instagram_profiles_found INTEGER DEFAULT 0,
                execution_time_seconds FLOAT,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,
                status VARCHAR(50) DEFAULT 'completed',
                notes TEXT
            );
            """
            
            # Índices para optimización
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_leads_source ON leads(source);",
                "CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);",
                "CREATE INDEX IF NOT EXISTS idx_leads_found_date ON leads(found_date);",
                "CREATE INDEX IF NOT EXISTS idx_leads_nombre ON leads(nombre);",
                "CREATE INDEX IF NOT EXISTS idx_emails_lead_id ON generated_emails(lead_id);",
                "CREATE INDEX IF NOT EXISTS idx_emails_status ON generated_emails(status);",
                "CREATE INDEX IF NOT EXISTS idx_sessions_type ON search_sessions(session_type);"
            ]
            
            # Ejecutar creación de tablas
            tables = [leads_table, emails_table, search_sessions_table]
            
            for i, table_sql in enumerate(tables, 1):
                result = self.execute_query(table_sql)
                if result is not None:
                    table_name = ["leads", "generated_emails", "search_sessions"][i-1]
                    logger.info(f"✅ Tabla {table_name} creada/verificada")
                else:
                    logger.error(f"❌ Error creando tabla {i}")
                    return False
            
            # Crear índices
            logger.info("🔍 Creando índices...")
            for index_sql in indexes:
                self.execute_query(index_sql)
            
            # Migrar tabla existente si es necesario
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
            
            # Verificar si existen las nuevas columnas
            migrations = [
                "ALTER TABLE leads ADD COLUMN IF NOT EXISTS linkedin_invite_sent BOOLEAN DEFAULT FALSE;",
                "ALTER TABLE leads ADD COLUMN IF NOT EXISTS linkedin_invite_date TIMESTAMP;",
                "ALTER TABLE leads ADD COLUMN IF NOT EXISTS linkedin_invite_status VARCHAR(50);",
                "ALTER TABLE leads ADD COLUMN IF NOT EXISTS instagram_invite_sent BOOLEAN DEFAULT FALSE;",
                "ALTER TABLE leads ADD COLUMN IF NOT EXISTS instagram_invite_date TIMESTAMP;",
                "ALTER TABLE leads ADD COLUMN IF NOT EXISTS instagram_invite_status VARCHAR(50);"
            ]
            
            for migration in migrations:
                result = self.execute_query(migration)
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
            # Buscar por nombre
            query = "SELECT id FROM leads WHERE nombre = %s"
            params = (nombre,)
            
            # Si hay website, también buscar por website
            if website and website.strip():
                query += " OR website = %s"
                params = (nombre, website)
            
            result = self.execute_query(query, params)
            
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
            
            result = self.execute_query(query, lead_data)
            
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
            
            result = self.execute_query(query, email_data)
            
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
            
            results = self.execute_query(query, params)
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
            
            results = self.execute_query(query, (lead_id,))
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
            
            result = self.execute_query(query, (status, lead_id))
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
            
            result = self.execute_query(query, (status, lead_id))
            return result is not None
            
        except Exception as e:
            logger.error(f"❌ Error actualizando status Instagram lead {lead_id}: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Obtener estadísticas de la base de datos."""
        try:
            stats = {}
            
            # Total leads
            result = self.execute_query("SELECT COUNT(*) as total FROM leads")
            stats['total_leads'] = result[0]['total'] if result else 0
            
            # Leads por fuente (filtrar NULLs)
            result = self.execute_query("""
                SELECT COALESCE(source, 'Sin fuente') as source, COUNT(*) as count 
                FROM leads 
                GROUP BY source
            """)
            stats['leads_by_source'] = {
                row['source']: row['count'] 
                for row in result if result
            } if result else {}
            
            # Leads por status (filtrar NULLs)
            result = self.execute_query("""
                SELECT COALESCE(status, 'Sin estado') as status, COUNT(*) as count 
                FROM leads 
                GROUP BY status
            """)
            stats['leads_by_status'] = {
                row['status']: row['count'] 
                for row in result if result
            } if result else {}
            
            # Total emails
            result = self.execute_query("SELECT COUNT(*) as total FROM generated_emails")
            stats['total_emails'] = result[0]['total'] if result else 0
            
            # Invitaciones LinkedIn enviadas
            result = self.execute_query("SELECT COUNT(*) as total FROM leads WHERE linkedin_invite_sent = true")
            stats['linkedin_invites_sent'] = result[0]['total'] if result else 0
            
            # Invitaciones Instagram enviadas
            result = self.execute_query("SELECT COUNT(*) as total FROM leads WHERE instagram_invite_sent = true")
            stats['instagram_invites_sent'] = result[0]['total'] if result else 0
            
            # Emails por status (filtrar NULLs)
            result = self.execute_query("""
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
    
    def test_connection(self) -> bool:
        """Probar conexión a la base de datos."""
        try:
            result = self.execute_query("SELECT 1 as test")
            if result and result[0]['test'] == 1:
                logger.info("✅ Test de conexión exitoso")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Test de conexión falló: {e}")
            return False
    
    def search_leads_by_keyword(self, keyword: str) -> List[Dict]:
        """Buscar leads que contengan una keyword específica."""
        if not self.connected:
            return []
        
        try:
            cursor = self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
            
            # Buscar en múltiples campos
            query = """
            SELECT * FROM leads 
            WHERE 
                LOWER(nombre) LIKE %s OR
                LOWER(descripcion) LIKE %s OR
                LOWER(url) LIKE %s OR
                LOWER(source) LIKE %s
            ORDER BY fecha_creacion DESC
            LIMIT 20
            """
            
            keyword_pattern = f"%{keyword.lower()}%"
            cursor.execute(query, (keyword_pattern, keyword_pattern, keyword_pattern, keyword_pattern))
            
            results = cursor.fetchall()
            cursor.close()
            
            # Convertir a lista de diccionarios
            leads = []
            for row in results:
                lead = dict(row)
                leads.append(lead)
            
            return leads
            
        except Exception as e:
            logger.error(f"Error buscando leads por keyword '{keyword}': {e}")
            return []

    def close(self):
        """Cerrar conexión a la base de datos."""
        if self.connection:
            self.connection.close()
            self.connected = False
            logger.info("🔒 Conexión PostgreSQL cerrada")
    
    def count_leads(self) -> int:
        """Contar total de leads en la base de datos."""
        try:
            if not self.connected:
                self.connect()
            
            cursor = self.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM leads")
            count = cursor.fetchone()[0]
            cursor.close()
            return count
        except Exception as e:
            logger.error(f"Error contando leads: {e}")
            return 0
    
    def save_lead(self, name: str, email: str = '', phone: str = '', url: str = '', 
                  description: str = '', source: str = '', keyword: str = '', 
                  industry: str = '') -> Optional[int]:
        """Wrapper simplificado para guardar lead con mapeo de columnas correcto."""
        lead_data = {
            'nombre': name,  # Mapear name -> nombre
            'email': email,
            'telefono': phone,  # Mapear phone -> telefono
            'website': url,  # Mapear url -> website
            'linkedin_url': url if 'linkedin.com' in url else '',  # Si es LinkedIn, también en linkedin_url
            'description': description,
            'source': source,
            'search_term': keyword,  # Mapear keyword -> search_term
            'productos_interes': industry  # Mapear industry -> productos_interes
        }
        
        # Limpiar campos vacíos
        clean_data = {k: v for k, v in lead_data.items() if v}
        
        return self.insert_lead(clean_data)
    
    def get_latest_leads(self, limit: int = 10) -> List[Dict]:
        """Obtener los últimos leads guardados con mapeo correcto de columnas."""
        try:
            if not self.connected:
                self.connect()
            
            cursor = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("""
                SELECT id, nombre as name, email, telefono as phone, 
                       COALESCE(linkedin_url, website) as url, website, linkedin_url,
                       description, search_term as keyword, productos_interes as industry, 
                       created_at, location, source
                FROM leads 
                ORDER BY created_at DESC 
                LIMIT %s
            """, (limit,))
            results = cursor.fetchall()
            cursor.close()
            
            # Convertir a lista de diccionarios
            return [dict(row) for row in results]
            
        except Exception as e:
            logger.error(f"Error obteniendo últimos leads: {e}")
            return []
    
    def save_manual_linkedin_lead(self, nombre: str, email: str = '', telefono: str = '', 
                                linkedin_url: str = '', description: str = '', 
                                industria: str = 'medical_aesthetics') -> Optional[int]:
        """
        Guardar lead de LinkedIn agregado manualmente.
        Esto permite trackear el flujo de ventas desde LinkedIn manual.
        """
        try:
            if not self.connected:
                self.connect()
            
            # Validar datos básicos
            if not nombre.strip():
                logger.error("Error: El nombre es obligatorio para guardar lead manual")
                return None
            
            # Preparar datos del lead manual
            lead_data = {
                'nombre': nombre.strip(),
                'email': email.strip() if email else '',
                'telefono': telefono.strip() if telefono else '',
                'linkedin_url': linkedin_url.strip() if linkedin_url else '',
                'description': description.strip() if description else 'Lead agregado manualmente',
                'source': 'LinkedIn (Manual)',  # Identificar como LinkedIn manual
                'productos_interes': industria,
                'status': 'pending',
                'extraction_method': 'manual_entry'
            }
            
            # Limpiar campos vacíos (excepto campos importantes)
            clean_data = {}
            for key, value in lead_data.items():
                if key in ['nombre', 'source', 'status', 'extraction_method', 'productos_interes'] or value:
                    clean_data[key] = value
            
            lead_id = self.insert_lead(clean_data)
            
            if lead_id:
                logger.info(f"✅ Lead manual de LinkedIn guardado: {nombre} (ID: {lead_id})")
                print(f"✅ Lead manual agregado exitosamente: {nombre}")
                print(f"   📞 Teléfono: {telefono if telefono else 'No proporcionado'}")
                print(f"   📧 Email: {email if email else 'No proporcionado'}")
                print(f"   🔗 LinkedIn: {linkedin_url if linkedin_url else 'No proporcionado'}")
                return lead_id
            else:
                logger.error(f"❌ Error al guardar lead manual: {nombre}")
                return None
                
        except Exception as e:
            logger.error(f"Error guardando lead manual de LinkedIn: {e}")
            print(f"❌ Error al guardar lead manual: {e}")
            return None

def test_database():
    """Función de prueba de la base de datos."""
    print("🧪 PROBANDO CONEXIÓN POSTGRESQL")
    print("="*40)
    
    db = Database()
    
    if not db.connected:
        print("❌ No se pudo conectar a PostgreSQL")
        print("💡 Verifica:")
        print("   • PostgreSQL está ejecutándose")
        print("   • pgAdmin está conectado")
        print("   • Credenciales en .env son correctas")
        return
    
    print("✅ Conexión establecida")
    
    # Test básico
    if db.test_connection():
        print("✅ Test de consulta exitoso")
    
    # Crear tablas
    if db.create_tables():
        print("✅ Tablas creadas/verificadas")
    
    # Obtener estadísticas
    stats = db.get_stats()
    print(f"\n📊 ESTADÍSTICAS:")
    print(f"   🏥 Total leads: {stats.get('total_leads', 0)}")
    print(f"   📧 Total emails: {stats.get('total_emails', 0)}")
    
    if stats.get('leads_by_source'):
        print(f"\n📋 Leads por fuente:")
        for source, count in stats['leads_by_source'].items():
            print(f"   • {source}: {count}")
    
    db.close()
    print("\n✅ Prueba de base de datos completada")

if __name__ == "__main__":
    test_database()