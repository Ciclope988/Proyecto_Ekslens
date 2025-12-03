"""
EKSLENS - API Routes
Rutas Flask para la API REST
"""

from flask import Blueprint, request, jsonify, render_template
import logging
from backend.services.lead_service import LeadService
from backend.services.search_service import SearchService

logger = logging.getLogger(__name__)

# Crear Blueprints
api_bp = Blueprint('api', __name__, url_prefix='/api')
web_bp = Blueprint('web', __name__)

# Instanciar servicios
lead_service = LeadService()
search_service = SearchService()


# ========== RUTAS WEB ==========

@web_bp.route('/')
def index():
    """Página principal."""
    return render_template('index.html')


# ========== RUTAS API ==========

@api_bp.route('/status')
def get_status():
    """Obtener estado actual del sistema."""
    try:
        status = search_service.get_system_status()
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/start_search', methods=['POST'])
def start_search():
    """Iniciar búsqueda de leads."""
    try:
        data = request.json
        result = search_service.start_search(data)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error starting search: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/stop_search', methods=['POST'])
def stop_search():
    """Detener búsqueda actual."""
    result = search_service.stop_search()
    return jsonify(result)


@api_bp.route('/results')
def get_results():
    """Obtener resultados de la última búsqueda."""
    try:
        results = search_service.get_latest_results()
        if not results:
            return jsonify({'message': 'No hay resultados disponibles'}), 404
        return jsonify(results)
    except Exception as e:
        logger.error(f"Error getting results: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/logs')
def get_logs():
    """Obtener logs en tiempo real."""
    logs = search_service.get_logs()
    return jsonify(logs)


@api_bp.route('/database_stats')
def get_database_stats():
    """Obtener estadísticas de la base de datos."""
    try:
        stats = lead_service.get_database_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/add_manual_lead', methods=['POST'])
def add_manual_lead():
    """Agregar lead de LinkedIn manualmente."""
    try:
        data = request.get_json()
        result = lead_service.add_manual_lead(data)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error adding manual lead: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/execute_query', methods=['POST'])
def execute_query():
    """Ejecutar consulta SQL personalizada (solo SELECT)."""
    try:
        data = request.get_json()
        result = lead_service.execute_custom_query(data.get('query', ''))
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/industries')
def get_available_industries():
    """Obtener industrias disponibles."""
    try:
        industries = search_service.get_available_industries()
        return jsonify(industries)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/change_industry', methods=['POST'])
def change_industry():
    """Cambiar industria activa."""
    try:
        data = request.get_json()
        result = search_service.change_industry(data.get('industry_type'))
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/industry_info')
def get_industry_info():
    """Obtener información de la industria actual."""
    try:
        info = search_service.get_industry_info()
        return jsonify(info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
