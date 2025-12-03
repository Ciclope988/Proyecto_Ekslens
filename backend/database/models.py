"""
EKSLENS - Database Models
Definición de tablas y esquemas de base de datos
"""

import logging
from typing import List

logger = logging.getLogger(__name__)


class DatabaseModels:
    """Definición de esquemas de base de datos."""
    
    @staticmethod
    def get_leads_table_schema() -> str:
        """Esquema de la tabla de leads."""
        return """
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
    
    @staticmethod
    def get_emails_table_schema() -> str:
        """Esquema de la tabla de emails generados."""
        return """
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
    
    @staticmethod
    def get_search_sessions_table_schema() -> str:
        """Esquema de la tabla de sesiones de búsqueda."""
        return """
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
    
    @staticmethod
    def get_indexes() -> List[str]:
        """Índices para optimización de consultas."""
        return [
            "CREATE INDEX IF NOT EXISTS idx_leads_source ON leads(source);",
            "CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);",
            "CREATE INDEX IF NOT EXISTS idx_leads_found_date ON leads(found_date);",
            "CREATE INDEX IF NOT EXISTS idx_leads_nombre ON leads(nombre);",
            "CREATE INDEX IF NOT EXISTS idx_emails_lead_id ON generated_emails(lead_id);",
            "CREATE INDEX IF NOT EXISTS idx_emails_status ON generated_emails(status);",
            "CREATE INDEX IF NOT EXISTS idx_sessions_type ON search_sessions(session_type);"
        ]
    
    @staticmethod
    def get_migrations() -> List[str]:
        """Migraciones para agregar nuevas columnas."""
        return [
            "ALTER TABLE leads ADD COLUMN IF NOT EXISTS linkedin_invite_sent BOOLEAN DEFAULT FALSE;",
            "ALTER TABLE leads ADD COLUMN IF NOT EXISTS linkedin_invite_date TIMESTAMP;",
            "ALTER TABLE leads ADD COLUMN IF NOT EXISTS linkedin_invite_status VARCHAR(50);",
            "ALTER TABLE leads ADD COLUMN IF NOT EXISTS instagram_invite_sent BOOLEAN DEFAULT FALSE;",
            "ALTER TABLE leads ADD COLUMN IF NOT EXISTS instagram_invite_date TIMESTAMP;",
            "ALTER TABLE leads ADD COLUMN IF NOT EXISTS instagram_invite_status VARCHAR(50);"
        ]
