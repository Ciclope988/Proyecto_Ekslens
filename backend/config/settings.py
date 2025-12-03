"""
EKSLENS - Configuración del Backend
"""

import os
from env_config import load_config

# Cargar configuración de entorno
config = load_config()

# Configuración de base de datos
DATABASE_CONFIG = {
    'host': config.get('DATABASE_HOST', 'localhost'),
    'port': int(config.get('DATABASE_PORT', 5433)),
    'database': config.get('DATABASE_NAME', 'ekslens_leads'),
    'user': config.get('DATABASE_USER', 'postgres'),
    'password': config.get('DATABASE_PASSWORD', '')
}

# Configuración de Flask
FLASK_CONFIG = {
    'SECRET_KEY': 'ekslens_secure_key_2024',
    'DEBUG': False,
    'HOST': 'localhost',
    'PORT': 5000
}

# Configuración de APIs
API_CONFIG = {
    'SERPAPI_KEY': config.get('SERPAPI_API_KEY', ''),
    'GEMINI_KEY': config.get('GEMINI_API_KEY', ''),
    'MAX_SEARCHES_PER_SESSION': 10,
    'MAX_CITIES': 5,
    'MAX_KEYWORDS': 10
}

# Configuración de logs
LOGGING_CONFIG = {
    'MAX_LOGS': 100,
    'LOG_LEVEL': 'INFO'
}
