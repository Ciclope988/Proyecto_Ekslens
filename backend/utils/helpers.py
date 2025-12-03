"""
EKSLENS - Utilidades y funciones auxiliares
"""

from datetime import datetime
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def format_date(date_obj: Optional[Any]) -> str:
    """
    Formatear objeto de fecha de forma segura.
    
    Args:
        date_obj: Objeto de fecha (datetime, str o None)
        
    Returns:
        Fecha formateada como string
    """
    if date_obj is None:
        return 'No disponible'
    
    if hasattr(date_obj, 'strftime'):
        return date_obj.strftime('%Y-%m-%d %H:%M')
    
    return str(date_obj)


def clean_dict(data: Dict, keep_empty: bool = False) -> Dict:
    """
    Limpiar diccionario eliminando valores vacíos.
    
    Args:
        data: Diccionario a limpiar
        keep_empty: Mantener valores vacíos
        
    Returns:
        Diccionario limpio
    """
    if keep_empty:
        return data
    
    return {k: v for k, v in data.items() if v or v == 0 or v == False}


def validate_query_safety(query: str) -> tuple[bool, str]:
    """
    Validar que una query SQL sea segura (solo SELECT).
    
    Args:
        query: Query SQL a validar
        
    Returns:
        Tupla (es_valida, mensaje_error)
    """
    if not query:
        return False, 'Query vacía'
    
    query = query.strip()
    
    # Solo permitir SELECT
    if not query.upper().startswith('SELECT'):
        return False, 'Solo se permiten consultas SELECT por seguridad'
    
    # Comandos peligrosos
    dangerous_keywords = [
        'INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 
        'CREATE', 'TRUNCATE', 'GRANT', 'REVOKE'
    ]
    
    query_upper = query.upper()
    for keyword in dangerous_keywords:
        if keyword in query_upper:
            return False, f'Comando {keyword} no permitido por seguridad'
    
    return True, ''


def log_operation(operation: str, details: Dict = None):
    """
    Registrar operación en log.
    
    Args:
        operation: Descripción de la operación
        details: Detalles adicionales
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_msg = f"[{timestamp}] {operation}"
    
    if details:
        log_msg += f" - {details}"
    
    logger.info(log_msg)


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncar texto a longitud máxima.
    
    Args:
        text: Texto a truncar
        max_length: Longitud máxima
        
    Returns:
        Texto truncado con '...' si es necesario
    """
    if not text:
        return ''
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length] + '...'
