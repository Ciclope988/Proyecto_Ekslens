"""
Manejo de variables de entorno para Ekslens.
Carga configuración desde .env y config.json con prioridad a .env
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

def load_env_file(env_path: str = '.env') -> Dict[str, str]:
    """Carga variables desde archivo .env"""
    env_vars = {}
    env_file = Path(env_path)
    
    if not env_file.exists():
        logger.warning(f"Archivo {env_path} no encontrado")
        return env_vars
    
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                # Ignorar líneas vacías y comentarios
                if not line or line.startswith('#'):
                    continue
                
                # Buscar formato KEY=VALUE
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Remover comillas si las tiene
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    env_vars[key] = value
        
        logger.info(f"✅ Cargadas {len(env_vars)} variables desde {env_path}")
        return env_vars
        
    except Exception as e:
        logger.error(f"Error cargando {env_path}: {e}")
        return env_vars

def get_config_with_env(config_file: str = 'config.json') -> Dict:
    """
    Carga configuración fusionando config.json con variables de entorno.
    Las variables de entorno tienen prioridad.
    """
    
    # 1. Cargar .env
    env_vars = load_env_file()
    
    # 2. Cargar config.json
    config = {}
    if Path(config_file).exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception as e:
            logger.error(f"Error cargando {config_file}: {e}")
            config = {}
    
    # 3. Aplicar variables de entorno con prioridad
    
    # Google Gemini API Key
    if 'GOOGLE_API_KEY' in env_vars:
        if 'llm' not in config:
            config['llm'] = {}
        config['llm']['api_key'] = env_vars['GOOGLE_API_KEY']
        logger.info("✅ API Key de Google Gemini cargada desde .env")
    
    # SerpApi Key
    if 'SERPAPI_KEY' in env_vars:
        config['serpapi_key'] = env_vars['SERPAPI_KEY']
        logger.info("✅ API Key de SerpApi cargada desde .env")
    
    # Bing Search API Key
    if 'BING_SEARCH_API_KEY' in env_vars:
        config['bing_search_api_key'] = env_vars['BING_SEARCH_API_KEY']
        logger.info("✅ API Key de Bing Search cargada desde .env")
    
    # Configuración de base de datos (DIRECTA y ANIDADA)
    if any(key.startswith('DATABASE_') for key in env_vars):
        if 'database' not in config:
            config['database'] = {}
        
        db_mappings = {
            'DATABASE_HOST': 'host',
            'DATABASE_PORT': 'port', 
            'DATABASE_NAME': 'name',
            'DATABASE_USER': 'user',
            'DATABASE_PASSWORD': 'password'
        }
        
        for env_key, config_key in db_mappings.items():
            if env_key in env_vars:
                # PONER EN AMBOS LUGARES para compatibilidad
                value = env_vars[env_key]
                if env_key == 'DATABASE_PORT':
                    value = int(value)
                    config['database'][config_key] = value
                    config[env_key] = value
                else:
                    config['database'][config_key] = value
                    config[env_key] = value  # DIRECTO para Database class
    
    # Credenciales de redes sociales
    social_mappings = {
        'LINKEDIN_EMAIL': 'LINKEDIN_EMAIL',
        'LINKEDIN_PASSWORD': 'LINKEDIN_PASSWORD',
        'INSTAGRAM_USERNAME': 'INSTAGRAM_USERNAME',
        'INSTAGRAM_PASSWORD': 'INSTAGRAM_PASSWORD'
    }
    
    for env_key, config_key in social_mappings.items():
        if env_key in env_vars and env_vars[env_key]:
            config[config_key] = env_vars[env_key]
            logger.info(f"✅ {env_key} cargada desde .env")
    
    # Información del remitente
    if any(key in env_vars for key in ['SENDER_NAME', 'COMPANY_NAME', 'PRODUCTS_FOCUS']):
        if 'contact' not in config:
            config['contact'] = {}
        if 'sender_info' not in config['contact']:
            config['contact']['sender_info'] = {}
        
        sender_mappings = {
            'SENDER_NAME': 'sender_name',
            'COMPANY_NAME': 'company_name',
            'PRODUCTS_FOCUS': 'products_focus'
        }
        
        for env_key, config_key in sender_mappings.items():
            if env_key in env_vars:
                config['contact']['sender_info'][config_key] = env_vars[env_key]
    
    # Configuración de email
    if any(key.endswith('_API_KEY') for key in env_vars):
        if 'email_service' not in config:
            config['email_service'] = {}
        
        if 'SENDGRID_API_KEY' in env_vars:
            config['email_service']['provider'] = 'sendgrid'
            config['email_service']['api_key'] = env_vars['SENDGRID_API_KEY']
        
        if 'FROM_EMAIL' in env_vars:
            config['email_service']['from_email'] = env_vars['FROM_EMAIL']
    
    # 4. Configuración por defecto si no existe
    ensure_default_config(config)
    
    return config

def ensure_default_config(config: Dict) -> None:
    """Asegura que la configuración tenga valores por defecto."""
    
    # LLM por defecto
    if 'llm' not in config:
        config['llm'] = {}
    
    llm_defaults = {
        'provider': 'gemini',
        'model': 'gemini-1.5-flash',
        'api_key': 'CONFIGURE_ME'
    }
    
    for key, value in llm_defaults.items():
        if key not in config['llm']:
            config['llm'][key] = value
    
    # Base de datos por defecto
    if 'database' not in config:
        config['database'] = {}
    
    db_defaults = {
        'type': 'postgresql',
        'host': 'localhost',
        'port': 5432,
        'name': 'ekslens_leads',
        'user': 'postgres',
        'password': 'your_password_here'
    }
    
    for key, value in db_defaults.items():
        if key not in config['database']:
            config['database'][key] = value
    
    # Búsqueda global por defecto
    if 'search' not in config:
        config['search'] = {
            'global_search': True,
            'use_specific_cities': False,
            'terminos_busqueda_globales': [
                'aesthetic clinic',
                'cosmetic surgery clinic',
                'medical spa',
                'clinica estetica',
                'medicina estetica'
            ]
        }
    
    # Contacto por defecto
    if 'contact' not in config:
        config['contact'] = {}
    
    if 'sender_info' not in config['contact']:
        config['contact']['sender_info'] = {
            'sender_name': 'CONFIGURE_ME',
            'company_name': 'CONFIGURE_ME',
            'products_focus': 'productos de medicina estética'
        }

def validate_config(config: Dict):
    """Valida la configuración y retorna lista de errores."""
    errors = []
    
    # Validar API Key de Gemini
    api_key = config.get('llm', {}).get('api_key', '')
    if not api_key or api_key == 'CONFIGURE_ME':
        errors.append("❌ Google Gemini API Key no configurada")
    elif len(api_key) < 30:
        errors.append("❌ Google Gemini API Key parece inválida (muy corta)")
    else:
        # Ocultar la mayor parte de la key para logging
        masked_key = f"{api_key[:10]}...{api_key[-4:]}"
        logger.info(f"✅ Google Gemini API Key válida: {masked_key}")
    
    # Validar configuración de BD
    db_config = config.get('database', {})
    required_db_fields = ['host', 'port', 'name', 'user', 'password']
    
    for field in required_db_fields:
        if not db_config.get(field):
            errors.append(f"❌ Campo de BD requerido: {field}")
        elif field == 'password' and db_config[field] == 'your_password_here':
            errors.append("❌ Password de BD no configurada")
    
    # Validar información del remitente
    sender_info = config.get('contact', {}).get('sender_info', {})
    required_sender_fields = ['sender_name', 'company_name']
    
    for field in required_sender_fields:
        if not sender_info.get(field) or sender_info[field] == 'CONFIGURE_ME':
            errors.append(f"❌ Información del remitente requerida: {field}")
    
    return errors

def get_environment_summary(config: Dict) -> str:
    """Retorna un resumen del entorno configurado."""
    summary = []
    
    # API Key status
    api_key = config.get('llm', {}).get('api_key', '')
    if api_key and api_key != 'CONFIGURE_ME':
        summary.append("✅ Google Gemini configurado")
    else:
        summary.append("❌ Google Gemini no configurado")
    
    # Database status
    db_config = config.get('database', {})
    if db_config.get('password', '') != 'your_password_here':
        summary.append(f"✅ PostgreSQL: {db_config.get('host')}:{db_config.get('port')}")
    else:
        summary.append("❌ PostgreSQL no configurado")
    
    # Sender info status
    sender_info = config.get('contact', {}).get('sender_info', {})
    if sender_info.get('sender_name', '') != 'CONFIGURE_ME':
        summary.append(f"✅ Remitente: {sender_info.get('sender_name')}")
    else:
        summary.append("❌ Información del remitente no configurada")
    
    return " | ".join(summary)

# Función helper para uso directo
def load_config(config_file: str = 'config.json') -> Dict:
    """
    Función principal para cargar configuración completa.
    Úsala en lugar de cargar config.json directamente.
    """
    return get_config_with_env(config_file)

# Test de la configuración
if __name__ == "__main__":
    print("🔧 TESTING CONFIGURACIÓN CON .ENV")
    print("=" * 50)
    
    config = load_config()
    errors = validate_config(config)
    
    print(f"\n📊 ESTADO: {get_environment_summary(config)}")
    
    if errors:
        print(f"\n❌ ERRORES ENCONTRADOS:")
        for error in errors:
            print(f"   {error}")
    else:
        print(f"\n✅ Configuración válida!")
    
    print(f"\n🔑 API Key detectada: {'✅ Sí' if config.get('llm', {}).get('api_key') != 'CONFIGURE_ME' else '❌ No'}")
    print(f"📧 Remitente: {config.get('contact', {}).get('sender_info', {}).get('sender_name', 'No configurado')}")
    print(f"🐘 Base de datos: {config.get('database', {}).get('host')}:{config.get('database', {}).get('port')}")