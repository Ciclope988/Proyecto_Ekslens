"""
EKSLENS - Web Interface Backend (Refactorizado)
Servidor Flask modularizado con arquitectura backend/frontend separada
"""

from flask import Flask
import logging
import shutil
import os
import atexit
from backend.api.routes import api_bp, web_bp
from backend.database.queries import DatabaseQueries

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear aplicación Flask
app = Flask(__name__, 
            template_folder='frontend/templates',
            static_folder='frontend/static')
app.secret_key = 'ekslens_secure_key_2024'

# Registrar Blueprints
app.register_blueprint(web_bp)
app.register_blueprint(api_bp)


def clean_pycache():
    """Limpiar todos los directorios __pycache__ al cerrar."""
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        count = 0
        for root, dirs, files in os.walk(base_dir):
            if '__pycache__' in dirs:
                pycache_path = os.path.join(root, '__pycache__')
                shutil.rmtree(pycache_path)
                count += 1
        if count > 0:
            print(f"\n🧹 {count} directorios __pycache__ eliminados")
    except Exception as e:
        print(f"\n⚠️ Error limpiando __pycache__: {e}")


# Registrar limpieza al cerrar
atexit.register(clean_pycache)


def main():
    """Función principal para ejecutar el servidor web."""
    print("🌐 INICIANDO EKSLENS WEB INTERFACE - ARQUITECTURA MODULAR")
    print("="*60)
    print("🎯 Interfaz gráfica para generación de leads por industrias")
    print("🔧 Servidor Flask con backend/frontend separados")
    print()
    print("📋 URLs disponibles:")
    print("   • Interfaz principal: http://localhost:5000")
    print("   • API status: http://localhost:5000/api/status")
    print("   • API industrias: http://localhost:5000/api/industries")
    print()
    print("⚠️ IMPORTANTE:")
    print("   • Mantén esta terminal abierta mientras usas la interfaz")
    print("   • Cierra con Ctrl+C cuando termines")
    print()
    
    # Verificar que los módulos estén disponibles
    try:
        db = DatabaseQueries()
        if db.db_conn.connected:
            print("✅ Base de datos conectada")
            db.close()
        else:
            print("⚠️ Base de datos no disponible")
    except Exception as e:
        print(f"⚠️ Base de datos no disponible: {e}")
    
    print("\n🚀 Iniciando servidor web...")
    print("📍 Abre tu navegador en: http://localhost:5000")
    print("="*50)
    
    # Ejecutar servidor Flask
    app.run(host='localhost', port=5000, debug=False, threaded=True)


if __name__ == "__main__":
    main()
