"""
EKSLENS - Scrapers Module
Módulo de scrapers especializados
"""

from .serpapi_scraper import SerpApiScraper
from .linkedin_scraper import LinkedInScraper

__all__ = ['SerpApiScraper', 'LinkedInScraper']