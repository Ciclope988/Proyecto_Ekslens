"""
EKSLENS - Database Connection (Compatibility Wrapper)
Wrapper para mantener compatibilidad con código existente mientras usamos el backend modularizado
"""

import logging
from backend.database.queries import DatabaseQueries

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Database(DatabaseQueries):
    """Clase de compatibilidad que hereda de DatabaseQueries."""
    
    def __init__(self):
        """Inicializar usando el nuevo módulo refactorizado."""
        super().__init__()
        # Mantener propiedades de compatibilidad
        self.connection = self.db_conn.connection
        self.connected = self.db_conn.connected
    
    def connect(self):
        """Wrapper para mantener compatibilidad."""
        result = self.db_conn.connect()
        self.connected = self.db_conn.connected
        return result
    
    def execute_query(self, query: str, params: tuple = None):
        """Wrapper para mantener compatibilidad."""
        return self.db_conn.execute_query(query, params)
    
    def test_connection(self):
        """Wrapper para mantener compatibilidad."""
        return self.db_conn.test_connection()


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
