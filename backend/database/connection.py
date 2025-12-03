"""
EKSLENS - Database Connection Module
Módulo de conexión a PostgreSQL
"""

import psycopg2
import psycopg2.extras
import logging
from typing import Optional, List, Dict, Any
from env_config import load_config

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Clase para manejar la conexión a PostgreSQL."""
    
    def __init__(self):
        """Inicializar configuración de conexión."""
        self.config = load_config()
        
        # Configuración de conexión
        self.host = self.config.get('DATABASE_HOST', 'localhost')
        self.port = int(self.config.get('DATABASE_PORT', 5433))
        self.database = self.config.get('DATABASE_NAME', 'ekslens_leads')
        self.user = self.config.get('DATABASE_USER', 'postgres')
        self.password = self.config.get('DATABASE_PASSWORD', '')
        
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
                # Logging de la consulta para debugging
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
            raise e
        except Exception as e:
            logger.error(f"❌ Error inesperado: {e}")
            raise e
    
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
    
    def close(self):
        """Cerrar conexión a la base de datos."""
        if self.connection:
            self.connection.close()
            self.connected = False
            logger.info("🔒 Conexión PostgreSQL cerrada")
