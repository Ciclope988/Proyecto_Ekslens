"""
EKSLENS - Web Interface Backend
Servidor Flask para interfaz web de generación de leads
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import json
import os
import threading
import time
from datetime import datetime
import logging
from typing import Dict, List

# Imports del sistema Ekslens
try:
    from database import Database
    from ekslens_lead_master_modular import EkslensLeadMaster
    # from search_optimizer import SearchOptimizer
    # from planificador_serpapi import get_monthly_usage_plan
except ImportError as e:
    print(f"⚠️ Error importando módulos: {e}")

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'ekslens_secure_key_2024'

# Estado global de la aplicación
app_state = {
    'is_running': False,
    'current_session': None,
    'last_results': None,
    'progress': 0,
    'status_message': 'Sistema listo',
    'logs': []
}

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

web_logger = WebLogger()

@app.route('/')
def index():
    """Página principal."""
    return render_template('index.html')

@app.route('/test-manual-lead')
def test_manual_lead():
    """Página de prueba para agregar leads manuales."""
    return render_template('test_manual_lead.html')

@app.route('/add-lead')
def add_lead():
    """Página principal para agregar leads manuales."""
    return render_template('add_lead.html')

@app.route('/manual-lead')
def manual_lead_simple():
    """Página simple para agregar leads manuales."""
    with open('manual_lead.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/api/status')
def get_status():
    """Obtener estado actual del sistema."""
    try:
        # Verificar conexión a base de datos
        db = Database()
        db_connected = db.test_connection() if db.connected else False
        
        if db.connected:
            stats = db.get_stats()
            db.close()
        else:
            stats = {}
        
        # Obtener plan mensual SerpApi
        try:
            # monthly_plan = get_monthly_usage_plan()
            monthly_plan = {'searches_remaining': 100, 'recommended_daily': 3}  # Placeholder
        except:
            monthly_plan = {'searches_remaining': 'Unknown', 'recommended_daily': 3}
        
        return jsonify({
            'is_running': app_state['is_running'],
            'progress': app_state['progress'],
            'status_message': app_state['status_message'],
            'database_connected': db_connected,
            'total_leads': stats.get('total_leads', 0),
            'total_emails': stats.get('total_emails', 0),
            'linkedin_invites_sent': stats.get('linkedin_invites_sent', 0),
            'instagram_invites_sent': stats.get('instagram_invites_sent', 0),
            'serpapi_remaining': monthly_plan.get('searches_remaining', 100),
            'recommended_daily': monthly_plan.get('recommended_daily', 3)
        })
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/optimize_search', methods=['POST'])
def optimize_search():
    """Optimizar búsqueda y mostrar configuración por ciudad."""
    try:
        data = request.get_json()
        cities = [city.strip() for city in data.get('cities', '').split(',') if city.strip()]
        keywords = [kw.strip() for kw in data.get('keywords', '').split(',') if kw.strip()]
        
        if not cities:
            return jsonify({'error': 'Por favor proporciona al menos una ciudad'}), 400
        
        if not keywords:
            return jsonify({'error': 'Por favor proporciona al menos una palabra clave'}), 400
        
        optimization_info = []
        
        for city in cities[:3]:  # Máximo 3 ciudades
            city_config = SearchOptimizer.get_city_config(city)
            search_terms = SearchOptimizer.generate_search_terms(city, max_terms=2)
            
            # Combinar keywords personalizadas con términos de búsqueda
            combined_terms = keywords + search_terms
            clinic_keywords = SearchOptimizer.get_clinic_keywords(city)
            
            optimization_info.append({
                'city': city,
                'location': city_config['location'],
                'country': city_config['country'],
                'language': city_config['hl'],
                'search_terms': combined_terms[:6],  # Mostrar hasta 6 términos
                'keywords': clinic_keywords[:5],  # Solo primeros 5 para display
                'total_keywords': len(clinic_keywords),
                'custom_keywords': keywords
            })
        
        return jsonify({
            'success': True,
            'optimization': optimization_info,
            'total_searches': len(cities),
            'total_keywords': len(keywords),
            'message': f'Búsqueda optimizada para {len(cities)} ciudad(es) con {len(keywords)} palabra(s) clave personalizada(s)'
        })
    
    except Exception as e:
        logger.error(f"Error optimizing search: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/start_search', methods=['POST'])
def start_search():
    """Iniciar búsqueda de leads."""
    if app_state['is_running']:
        return jsonify({'error': 'Ya hay una búsqueda en progreso'}), 400
    
    try:
        data = request.json
        cities = data.get('cities', ['madrid', 'barcelona', 'valencia'])
        keywords = data.get('keywords', ['botox', 'dermal fillers', 'aesthetic supplies'])
        max_searches = int(data.get('max_searches', 3))
        use_serpapi = data.get('use_serpapi', True)
        use_linkedin = data.get('use_linkedin', True)
        use_instagram = data.get('use_instagram', False)
        
        # Validaciones
        if max_searches > 10:
            return jsonify({'error': 'Máximo 10 búsquedas permitidas'}), 400
        
        if len(cities) > 5:
            return jsonify({'error': 'Máximo 5 ciudades permitidas'}), 400
        
        if len(keywords) > 10:
            return jsonify({'error': 'Máximo 10 palabras clave permitidas'}), 400
        
        # Iniciar búsqueda en hilo separado
        search_thread = threading.Thread(
            target=run_search_process,
            args=(cities, keywords, max_searches, use_serpapi, use_linkedin, use_instagram)
        )
        search_thread.start()
        
        app_state['is_running'] = True
        app_state['progress'] = 0
        app_state['status_message'] = 'Iniciando búsqueda...'
        web_logger.clear_logs()
        web_logger.add_log('INFO', f'Búsqueda iniciada: {len(cities)} ciudades, {len(keywords)} keywords, {max_searches} búsquedas')
        
        return jsonify({'message': 'Búsqueda iniciada correctamente'})
        
    except Exception as e:
        logger.error(f"Error starting search: {e}")
        return jsonify({'error': str(e)}), 500

def run_search_process(cities: List[str], keywords: List[str], max_searches: int, use_serpapi: bool, use_linkedin: bool, use_instagram: bool):
    """Ejecutar proceso de búsqueda en segundo plano."""
    try:
        web_logger.add_log('INFO', '🚀 Iniciando EKSLENS Lead Master')
        app_state['status_message'] = 'Configurando sistema...'
        app_state['progress'] = 10
        
        # Crear instancia del Lead Master (arquitectura modular)
        master = EkslensLeadMaster('medical_aesthetics')
        
        # Configurar búsqueda
        web_logger.add_log('INFO', f'📍 Ciudades: {", ".join(cities)}')
        web_logger.add_log('INFO', f'🔍 Keywords: {", ".join(keywords)}')
        web_logger.add_log('INFO', f'🔍 SerpApi: {"✅" if use_serpapi else "❌"}')
        web_logger.add_log('INFO', f'🔍 Búsquedas SerpApi: {max_searches}')
        web_logger.add_log('INFO', f'🔗 LinkedIn: {"✅" if use_linkedin else "❌"}')
        
        app_state['progress'] = 20
        app_state['status_message'] = 'Ejecutando búsquedas...'
        
        # Ejecutar búsqueda con keywords personalizadas
        results = master.run_master_search_with_keywords(
            cities=cities, 
            keywords=keywords,
            max_searches=max_searches,
            use_serpapi=use_serpapi,
            use_linkedin=use_linkedin
        )
        
        app_state['progress'] = 90
        app_state['status_message'] = 'Finalizando...'
        
        # Guardar resultados
        app_state['last_results'] = results
        app_state['progress'] = 100
        app_state['status_message'] = f'✅ Completado: {results.get("total_leads", 0)} leads encontrados'
        
        web_logger.add_log('SUCCESS', f'🎯 Búsqueda completada exitosamente')
        web_logger.add_log('INFO', f'📊 Total leads: {results.get("total_leads", 0)}')
        web_logger.add_log('INFO', f'📧 Emails generados: {len(results.get("ai_emails", []))}')
        
        # Guardar log de sesión
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        log_file = f'web_session_{timestamp}.json'
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)
        
        web_logger.add_log('INFO', f'📄 Log guardado: {log_file}')
        
    except Exception as e:
        error_msg = f'❌ Error en búsqueda: {str(e)}'
        web_logger.add_log('ERROR', error_msg)
        app_state['status_message'] = error_msg
        app_state['progress'] = 0
    
    finally:
        app_state['is_running'] = False

@app.route('/api/results')
def get_results():
    """Obtener resultados de la última búsqueda."""
    if not app_state['last_results']:
        return jsonify({'message': 'No hay resultados disponibles'}), 404
    
    results = app_state['last_results']
    
    # Formatear resultados para la web
    formatted_results = {
        'total_leads': results.get('total_leads', 0),
        'serpapi_leads': len(results.get('serpapi_results', [])),
        'linkedin_leads': len(results.get('linkedin_results', [])),
        'ai_emails': len(results.get('ai_emails', [])),
        'execution_summary': results.get('execution_summary', {}),
        'sample_leads': []
    }
    
    # Mostrar muestra de leads (primeros 5)
    all_leads = results.get('serpapi_results', []) + results.get('linkedin_results', [])
    for lead in all_leads[:5]:
        formatted_lead = {
            'name': lead.get('nombre', 'Sin nombre'),
            'source': lead.get('source', 'Desconocido'),
            'website': lead.get('website', ''),
            'description': lead.get('description', '')[:100] + '...' if len(lead.get('description', '')) > 100 else lead.get('description', '')
        }
        formatted_results['sample_leads'].append(formatted_lead)
    
    return jsonify(formatted_results)

@app.route('/api/logs')
def get_logs():
    """Obtener logs en tiempo real."""
    return jsonify({
        'logs': web_logger.get_logs(),
        'is_running': app_state['is_running'],
        'progress': app_state['progress'],
        'status_message': app_state['status_message']
    })

@app.route('/api/database_stats')
def get_database_stats():
    """Obtener estadísticas de la base de datos."""
    try:
        db = Database()
        
        if not db.connected:
            return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500
        
        stats = db.get_stats()
        
        # Obtener leads recientes
        recent_leads = db.get_leads(limit=10)
        
        formatted_stats = {
            'total_leads': stats.get('total_leads', 0),
            'total_emails': stats.get('total_emails', 0),
            'leads_by_source': stats.get('leads_by_source', {}),
            'leads_by_status': stats.get('leads_by_status', {}),
            'recent_leads': []
        }
        
        # Formatear leads recientes
        for lead in recent_leads:
            # Manejar fechas de forma segura
            found_date = lead.get('found_date') or lead.get('fecha_creacion')
            if found_date and hasattr(found_date, 'strftime'):
                date_str = found_date.strftime('%Y-%m-%d %H:%M')
            elif found_date:
                date_str = str(found_date)
            else:
                date_str = 'No disponible'
            
            formatted_lead = {
                'id': lead.get('id'),
                'name': lead.get('nombre') or lead.get('nombre', 'Sin nombre'),
                'source': lead.get('source', 'Desconocido'),
                'status': lead.get('status') or lead.get('estado', 'pending'),
                'found_date': date_str,
                'linkedin_url': lead.get('linkedin_url', ''),
                'website': lead.get('website', ''),
                'email': lead.get('email', ''),
                'telefono': lead.get('telefono', ''),
                'phone': lead.get('phone', '')  # Para compatibilidad
            }
            formatted_stats['recent_leads'].append(formatted_lead)
        
        db.close()
        return jsonify(formatted_stats)
        
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stop_search', methods=['POST'])
def stop_search():
    """Detener búsqueda actual (solo cambia el estado)."""
    app_state['is_running'] = False
    app_state['status_message'] = 'Búsqueda detenida por el usuario'
    web_logger.add_log('WARNING', 'Búsqueda detenida por el usuario')
    return jsonify({'message': 'Búsqueda detenida'})

@app.route('/api/send_linkedin_invites', methods=['POST'])
def send_linkedin_invites():
    """Enviar invitaciones personalizadas por LinkedIn."""
    try:
        data = request.get_json()
        leads_to_invite = data.get('leads', [])
        custom_message = data.get('message', '')
        
        if not leads_to_invite:
            return jsonify({'error': 'No se especificaron leads para invitar'}), 400
        
        web_logger.add_log('INFO', f'🔗 Iniciando envío de {len(leads_to_invite)} invitaciones LinkedIn')
        
        # Ejecutar en hilo separado para no bloquear la interfaz
        def send_invites_async():
            try:
                lead_master = EkslensLeadMaster('medical_aesthetics')
                results = lead_master.send_linkedin_invitations(leads_to_invite, custom_message)
                
                app_state['linkedin_invite_results'] = results
                web_logger.add_log('SUCCESS', f'✅ Invitaciones LinkedIn enviadas: {results.get("sent", 0)}/{len(leads_to_invite)}')
                
            except Exception as e:
                web_logger.add_log('ERROR', f'❌ Error enviando invitaciones: {e}')
        
        # Iniciar proceso asíncrono
        thread = threading.Thread(target=send_invites_async)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'message': 'Proceso de invitaciones iniciado',
            'leads_count': len(leads_to_invite)
        })
        
    except Exception as e:
        logger.error(f"Error en send_linkedin_invites: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/linkedin_invite_results')
def get_linkedin_invite_results():
    """Obtener resultados de las invitaciones LinkedIn."""
    results = app_state.get('linkedin_invite_results', {
        'sent': 0,
        'failed': 0,
        'total': 0,
        'details': []
    })
    return jsonify(results)

@app.route('/api/industries')
def get_available_industries():
    """Obtener industrias disponibles."""
    try:
        master = EkslensLeadMaster()
        industries = master.get_available_industries()
        
        return jsonify({
            'industries': industries,
            'current': master.industry.name if hasattr(master, 'industry') else 'medical_aesthetics'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/change_industry', methods=['POST'])
def change_industry():
    """Cambiar industria activa."""
    try:
        data = request.get_json()
        industry_type = data.get('industry_type')
        
        if not industry_type:
            return jsonify({'error': 'industry_type requerido'}), 400
        
        # Crear nueva instancia con industria específica
        master = EkslensLeadMaster(industry_type)
        info = master.get_industry_info()
        
        web_logger.add_log('INFO', f'🔄 Industria cambiada a: {info["name"]}')
        
        return jsonify({
            'message': f'Industria cambiada a {info["name"]}',
            'industry_info': info
        })
        
    except Exception as e:
        web_logger.add_log('ERROR', f'Error cambiando industria: {e}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/industry_info')
def get_industry_info():
    """Obtener información de la industria actual."""
    try:
        master = EkslensLeadMaster()
        info = master.get_industry_info()
        
        return jsonify(info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/add_manual_lead', methods=['POST'])
def add_manual_lead():
    """Agregar lead de LinkedIn manualmente."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No se recibieron datos'}), 400
        
        # Validar datos requeridos
        nombre = data.get('nombre', '').strip()
        if not nombre:
            return jsonify({'error': 'El nombre es obligatorio'}), 400
        
        # Obtener datos opcionales
        email = data.get('email', '').strip()
        telefono = data.get('telefono', '').strip()
        linkedin_url = data.get('linkedin_url', '').strip()
        description = data.get('description', '').strip()
        industria = data.get('industria', 'medical_aesthetics')
        
        # Guardar en base de datos
        db = Database()
        if not db.connected:
            return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500
        
        lead_id = db.save_manual_linkedin_lead(
            nombre=nombre,
            email=email, 
            telefono=telefono,
            linkedin_url=linkedin_url,
            description=description,
            industria=industria
        )
        
        db.close()
        
        if lead_id:
            return jsonify({
                'success': True,
                'message': f'Lead "{nombre}" agregado exitosamente',
                'lead_id': lead_id
            })
        else:
            return jsonify({'error': 'Error al guardar el lead en la base de datos'}), 500
            
    except Exception as e:
        logger.error(f"Error agregando lead manual: {e}")
        return jsonify({'error': f'Error interno: {str(e)}'}), 500

@app.route('/api/execute_query', methods=['POST'])
def execute_query():
    """Ejecutar consulta SQL personalizada (solo SELECT por seguridad)."""
    try:
        data = request.get_json()
        
        if not data or not data.get('query'):
            return jsonify({'error': 'No se proporcionó consulta SQL'}), 400
        
        query = data.get('query').strip()
        
        # Validación de seguridad: solo permitir SELECT
        if not query.upper().startswith('SELECT'):
            return jsonify({'error': 'Solo se permiten consultas SELECT por seguridad'}), 400
        
        # Verificar que no contenga comandos peligrosos
        dangerous_keywords = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 'CREATE', 'TRUNCATE', 'GRANT', 'REVOKE']
        query_upper = query.upper()
        
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                return jsonify({'error': f'Comando {keyword} no permitido por seguridad'}), 400
        
        # Conectar a base de datos
        db = Database()
        if not db.connected:
            return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500
        
        # Ejecutar consulta
        try:
            results = db.execute_query(query)
            
            if results:
                # Obtener nombres de columnas del primer resultado
                columns = list(results[0].keys()) if results else []
                
                return jsonify({
                    'success': True,
                    'results': results,
                    'columns': columns,
                    'count': len(results)
                })
            else:
                return jsonify({
                    'success': True,
                    'results': [],
                    'columns': [],
                    'count': 0
                })
                
        except Exception as query_error:
            logger.error(f"Error ejecutando consulta: {query_error}")
            return jsonify({'error': f'Error en consulta: {str(query_error)}'}), 400
        
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error en execute_query: {e}")
        return jsonify({'error': f'Error interno: {str(e)}'}), 500

def main():
    """Función principal para ejecutar el servidor web."""
    print("🌐 INICIANDO EKSLENS WEB INTERFACE - ARQUITECTURA MODULAR")
    print("="*60)
    print("🎯 Interfaz gráfica para generación de leads por industrias")
    print("🔧 Servidor Flask en modo local")
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
        db = Database()
        if db.connected:
            print("✅ Base de datos conectada")
            db.close()
        else:
            print("⚠️ Base de datos no disponible")
    except:
        print("⚠️ Base de datos no disponible")
    
    print("\n🚀 Iniciando servidor web...")
    print("📍 Abre tu navegador en: http://localhost:5000")
    print("="*50)
    
    # Ejecutar servidor Flask
    app.run(host='localhost', port=5000, debug=False, threaded=True)

if __name__ == "__main__":
    main()