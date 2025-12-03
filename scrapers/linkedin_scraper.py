"""
EKSLENS - LinkedIn Scraper
Scraper especializado para LinkedIn con configuración por industria
"""

import time
import random
import logging
from typing import List, Dict, Optional
from datetime import datetime
from industries.base_industry import BaseIndustry

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
except ImportError:
    print("⚠️ Selenium no disponible - LinkedIn scraping deshabilitado")

logger = logging.getLogger(__name__)


class LinkedInScraper:
    """Scraper especializado para LinkedIn con configuración por industria."""
    
    def __init__(self, email: str, password: str, industry: BaseIndustry):
        self.email = email
        self.password = password
        self.industry = industry
        self.driver = None
        self.session_active = False
        self.used_search_terms = set()
        
        # Configurar opciones Chrome stealth
        self.chrome_options = Options()
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Configuraciones adicionales para estabilidad
        self.chrome_options.add_argument("--disable-web-security")
        self.chrome_options.add_argument("--allow-running-insecure-content")
        self.chrome_options.add_argument("--disable-extensions")
        self.chrome_options.add_argument("--disable-plugins")
        self.chrome_options.add_argument("--disable-images")  # Faster loading
        self.chrome_options.add_argument("--window-size=1920,1080")
        
        # User agent rotating
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
        ]
        self.chrome_options.add_argument(f'--user-agent={random.choice(user_agents)}')
    
    def search_by_keywords(self, cities: List[str], keywords: List[str]) -> List[Dict]:
        """Ejecutar búsquedas LinkedIn con keywords personalizadas."""
        leads = []
        
        if not self.email or not self.password:
            print("⚠️ LinkedIn no disponible - faltan credenciales")
            return leads
        
        print(f"\n🔗 INICIANDO LINKEDIN SCRAPER - BÚSQUEDA SIMPLIFICADA")
        print(f"📋 Industria: {self.industry.name}")
        print(f"🎯 Keywords: {', '.join(keywords[:3])}{'...' if len(keywords) > 3 else ''}")
        print(f"💡 Estrategia: Términos SIMPLES (ej: 'Radiesse madrid' en lugar de combinaciones complejas)")
        
        try:
            if self.start_session():
                print("✅ LinkedIn login exitoso")
                
                for city in cities[:2]:  # Máximo 2 ciudades
                    print(f"\n🔍 Buscando en {city.upper()}")
                    
                    city_companies = self._search_city_with_keywords(city, keywords)
                    leads.extend(city_companies)
                    
                    time.sleep(5)  # Pausa entre ciudades
                
                self.close_session()
            else:
                print("❌ Error en login LinkedIn")
        
        except Exception as e:
            logger.error(f"Error en LinkedIn scraper: {e}")
            print(f"❌ Error en LinkedIn: {e}")
        
        print(f"\n📊 LinkedIn completado: {len(leads)} leads totales")
        return leads
    
    def start_session(self) -> bool:
        """Iniciar sesión LinkedIn."""
        try:
            self.driver = webdriver.Chrome(options=self.chrome_options)
            
            # Script anti-detección
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.driver.get("https://www.linkedin.com/login")
            time.sleep(3)
            
            # Login
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            password_field = self.driver.find_element(By.ID, "password")
            
            email_field.send_keys(self.email)
            password_field.send_keys(self.password)
            
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            time.sleep(5)
            
            # Verificar login exitoso
            current_url = self.driver.current_url
            if "feed" in current_url or "mynetwork" in current_url or "in/" in current_url:
                self.session_active = True
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error en login LinkedIn: {e}")
            return False
    
    def close_session(self):
        """Cerrar sesión LinkedIn."""
        if self.driver:
            self.driver.quit()
            self.session_active = False
    
    def _search_city_with_keywords(self, city: str, keywords: List[str]) -> List[Dict]:
        """Buscar empresas en una ciudad con keywords específicas."""
        companies = []
        
        # Crear términos de búsqueda combinando keywords con términos de la industria
        search_terms = self._generate_search_terms(city, keywords)
        
        print(f"   📋 Probando {len(search_terms)} términos de búsqueda...")
        
        for i, search_term in enumerate(search_terms, 1):
            print(f"   🔍 Término {i}: '{search_term}'")
            
            try:
                # Verificar si ya usamos este término
                term_key = f"{city}_{search_term}".lower()
                if term_key in self.used_search_terms:
                    print(f"   ⚠️ Término ya utilizado, saltando...")
                    continue
                
                self.used_search_terms.add(term_key)
                
                # Crear URL simple para LinkedIn People Search con parámetros de diversificación
                # En lugar de usar industry.get_linkedin_search_url() que es compleja
                encoded_term = search_term.replace(' ', '%20')
                
                # ESTRATEGIA DE PAGINACIÓN + DIVERSIFICACIÓN
                # LinkedIn usa &start=0, &start=10, &start=20, etc. para paginación
                pages_to_search = [0, 10, 20]  # Páginas 1, 2, 3
                
                # ESTRATEGIA DE DIVERSIFICACIÓN: Usar diferentes parámetros cada vez
                diversification_params = [
                    "",  # Búsqueda normal
                    "&sortBy=relevance",
                    "&facetGeoRegion=%5B%22es%3A2%22%5D",  # España 
                ]
                
                # Elegir parámetro según el índice para variedad
                param_index = (i - 1) % len(diversification_params)
                diversity_param = diversification_params[param_index]
                
                # Buscar en múltiples páginas para este término
                for page_start in pages_to_search:
                    pagination_param = f"&start={page_start}"
                    search_url = f"https://www.linkedin.com/search/results/people/?keywords={encoded_term}&origin=GLOBAL_SEARCH_HEADER{diversity_param}{pagination_param}"
                    
                    print(f"   🌐 URL (página {page_start//10 + 1}): {search_url[:80]}...")
                    print(f"   📄 Buscando desde resultado #{page_start + 1}")
                    
                    # Ejecutar búsqueda en esta página
                    page_results = self._execute_linkedin_search(search_url, f"{search_term} (p{page_start//10 + 1})")
                    companies.extend(page_results)
                    
                    print(f"   ✅ {len(page_results)} resultados en página {page_start//10 + 1}")
                    
                    # Si no hay resultados en esta página, no buscar más páginas
                    if not page_results:
                        print(f"   ⚠️ No hay más resultados para '{search_term}', saltando páginas restantes")
                        break
                    
                    time.sleep(random.uniform(3, 6))  # Pausa entre páginas
                
                print(f"   📊 Total empresas encontradas para '{search_term}': {sum(len(r) for r in [companies[-len(page_results):] for page_results in [companies]])}")
                time.sleep(random.uniform(6, 10))  # Pausa más larga entre términos de búsqueda
                
            except Exception as e:
                print(f"   ❌ Error en '{search_term}': {str(e)}")
                continue
        
        # Eliminar duplicados
        unique_companies = self._remove_duplicates(companies)
        print(f"   📊 Total empresas únicas: {len(unique_companies)}")
        
        return unique_companies[:15]  # Máximo 15 por ciudad
    
    def _generate_search_terms(self, city: str, keywords: List[str]) -> List[str]:
        """Generar términos de búsqueda SIMPLES con mayor diversidad."""
        search_terms = []
        
        # Usar hasta 3 keywords principales - BÚSQUEDA SIMPLE
        selected_keywords = keywords[:3]
        
        for keyword in selected_keywords:
            # 1. SIMPLE: Solo keyword + ciudad (sin términos complejos)
            simple_term = f"{keyword.strip()} {city.strip()}"
            search_terms.append(simple_term)
            
            # 2. Solo keyword (sin ciudad) para perfiles remotos
            if len(keyword.strip()) > 4:  # Solo si keyword es lo suficientemente específica
                search_terms.append(keyword.strip())
            
            # 3. DIVERSIFICACIÓN: Agregar variaciones de la keyword
            keyword_variations = self._get_keyword_variations(keyword.strip(), city.strip())
            search_terms.extend(keyword_variations)
        
        print(f"   🎯 Términos DIVERSOS generados: {search_terms}")
        return search_terms[:8]  # Máximo 8 términos diversos
    
    def _get_keyword_variations(self, keyword: str, city: str) -> List[str]:
        """Generar variaciones de keyword para mayor diversidad."""
        variations = []
        
        # Variaciones específicas por industria
        if hasattr(self.industry, 'get_keyword_variations'):
            variations.extend(self.industry.get_keyword_variations(keyword))
        
        # Variaciones genéricas
        generic_variations = [
            f"especialista {keyword} {city}",
            f"doctor {keyword} {city}",
            f"profesional {keyword}",
            f"clínica {keyword} {city}",
        ]
        
        # Solo agregar si la keyword es específica de medicina estética
        if keyword.lower() in ['botox', 'radiesse', 'ácido hialurónico', 'fillers']:
            variations.extend(generic_variations[:2])  # Solo las 2 primeras
        
        return variations[:2]  # Máximo 2 variaciones por keyword
        
        print(f"   🎯 Términos SIMPLES generados: {search_terms}")
        return search_terms[:4]  # Máximo 4 términos simples
    
    def _execute_linkedin_search(self, search_url: str, search_term: str) -> List[Dict]:
        """Ejecutar búsqueda individual en LinkedIn."""
        people = []
        
        try:
            self.driver.get(search_url)
            time.sleep(random.uniform(3, 6))
            
            # Scroll para cargar contenido
            for _ in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(2, 4))
            
            # Extraer personas usando selectores modernos
            self._current_keyword = search_term  # Para el método _extract_person_data
            people = self._extract_person_data(self.driver)
            
        except Exception as e:
            logger.error(f"Error en búsqueda LinkedIn '{search_term}': {e}")
        
        return people
    
    def _extract_companies_from_page(self, search_term: str) -> List[Dict]:
        """Extraer personas/empresas de la página actual con selectores actualizados."""
        companies = []
        
        # Selectores actualizados para búsqueda de PERSONAS en LinkedIn (2025)
        selectors = [
            '.reusable-search__result-container',
            '[data-chameleon-result-urn]',
            '.search-results-container .entity-result',
            '.entity-result__content'
        ]
        
        print(f"   👁️ Buscando elementos en página...")
        
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"   📋 Encontrados {len(elements)} elementos con selector '{selector}'")
                
                for i, element in enumerate(elements[:8]):  # Máximo 8 por selector
                    try:
                        person_data = self._extract_person_data(element, search_term, i+1)
                        if person_data and self._is_valid_lead(person_data):
                            companies.append(person_data)
                            print(f"   ✅ Lead #{i+1}: {person_data['name'][:30]}...")
                    except Exception as e:
                        print(f"   ⚠️ Error extrayendo elemento #{i+1}: {e}")
                        continue
                
                if companies:
                    print(f"   🎯 Encontrados {len(companies)} leads válidos")
                    break  # Si encontramos personas, no usar más selectores
                    
            except Exception as e:
                print(f"   ❌ Error con selector '{selector}': {e}")
                continue
        
        return companies
    
    def _extract_person_data(self, element, search_term: str, index: int) -> Optional[Dict]:
        """Extraer datos de una persona/profesional individual."""
        # Selectores para nombre y URL de PERSONAS
        name_selectors = [
            '.entity-result__title-text a .visually-hidden',
            '.app-aware-link .visually-hidden', 
            'h3 .visually-hidden',
            '.entity-result__title-text a',
            'h3 a span[aria-hidden="true"]'
        ]
        
        name = None
        linkedin_url = None
        
        # Intentar extraer nombre y URL
        for selector in name_selectors:
            try:
                name_element = element.find_element(By.CSS_SELECTOR, selector)
                name = name_element.text.strip()
                if name:
                    # Buscar el link padre
                    link_element = name_element.find_element(By.XPATH, ".//ancestor::a")
                    linkedin_url = link_element.get_attribute('href')
                    break
            except:
                continue
        
        # Fallback: buscar link directo
        if not linkedin_url:
            try:
                link_element = element.find_element(By.CSS_SELECTOR, '.app-aware-link, .entity-result__title-text a, h3 a')
                linkedin_url = link_element.get_attribute('href')
                if not name:
                    name = link_element.text.strip()
            except:
                pass
        
        if not name or not linkedin_url or len(name) < 2:
            return None
        
        # Extraer información profesional
        job_selectors = [
            '.entity-result__primary-subtitle',
            '.entity-result__summary',
            '[data-field="headline"]'
        ]
        
        job_title = ""
        company_name = ""
        
        for selector in job_selectors:
            try:
                job_element = element.find_element(By.CSS_SELECTOR, selector)
                job_text = job_element.text.strip()
                
                # Separar título y empresa si está en formato "Título at Empresa"
                if " at " in job_text:
                    parts = job_text.split(" at ", 1)
                    job_title = parts[0].strip()
                    company_name = parts[1].strip()
                else:
                    job_title = job_text
                
                if job_title:
                    break
            except:
                continue
        
        # Extraer ubicación
        location = ""
        location_selectors = [
            '.entity-result__secondary-subtitle',
            '[data-field="location"]'
        ]
        
        for selector in location_selectors:
            try:
                location_element = element.find_element(By.CSS_SELECTOR, selector)
                location = location_element.text.strip()
                if location:
                    break
            except:
                continue
        
        return {
            'name': name,
            'job_title': job_title,
            'company_name': company_name or f"Empresa #{index}",
            'location': location,
            'linkedin_url': linkedin_url,
            'description': f"{job_title} en {company_name}" if job_title and company_name else job_title,
            'source': 'LinkedIn People Search',
            'keyword_used': search_term.split()[0],  # Primera palabra del término
            'extraction_method': 'simple-search',
            'found_date': datetime.now(),
            'industry': self.industry.name,
            'search_term_full': search_term
        }
    
    def _is_valid_lead(self, person_data: Dict) -> bool:
        """Validación simple para personas/leads."""
        # Verificar campos mínimos
        if not person_data.get('name') or not person_data.get('linkedin_url'):
            return False
        
        # Verificar que el nombre tenga al menos 2 caracteres
        if len(person_data['name']) < 2:
            return False
        
        # Verificar que la URL sea de LinkedIn
        url = person_data.get('linkedin_url', '')
        if not ('linkedin.com/in/' in url or 'linkedin.com/pub/' in url):
            return False
        
        return True
    
    def _extract_company_data(self, element, search_term: str) -> Optional[Dict]:
        """Método legacy - mantenido para compatibilidad."""
        return self._extract_person_data(element, search_term, 1)
    
    def _remove_duplicates(self, companies: List[Dict]) -> List[Dict]:
        """Eliminar duplicados basado en nombre y URL."""
        seen_names = set()
        seen_urls = set()
        unique_companies = []
        
        for company in companies:
            name_key = company.get('name', '').lower().strip()
            url_key = company.get('linkedin_url', '').lower()
            
            if name_key not in seen_names and url_key not in seen_urls:
                unique_companies.append(company)
                seen_names.add(name_key)
                seen_urls.add(url_key)
        
        return unique_companies
    def _extract_person_data(self, driver):
        """Extraer datos de personas usando estrategia robusta de enlaces."""
        people_data = []
        
        print("   🔍 EXTRACCIÓN ROBUSTA - Buscando enlaces de perfil...")
        
        try:
            # ESTRATEGIA MEJORADA: Filtrar solo resultados de búsqueda
            # Primero buscar contenedores de resultados específicos
            search_containers = []
            search_selectors = [
                '.reusable-search__result-container',
                '[data-chameleon-result-urn]', 
                '.entity-result',
                '.search-results-container .entity-result__content'
            ]
            
            for selector in search_selectors:
                try:
                    containers = driver.find_elements(By.CSS_SELECTOR, selector)
                    search_containers.extend(containers)
                    if containers:
                        print(f"   📋 {len(containers)} contenedores encontrados con: {selector}")
                except:
                    continue
            
            if not search_containers:
                print("   ⚠️ No se encontraron contenedores de resultados, usando método alternativo...")
                # Fallback: buscar enlaces pero con filtros más estrictos
                all_links = driver.find_elements(By.TAG_NAME, "a")
                search_containers = []
                for link in all_links:
                    href = link.get_attribute('href')
                    if href and '/in/' in href and '/company/' not in href and '/school/' not in href:
                        # Verificar que no sea parte de "contactos en común"
                        try:
                            parent_text = link.find_element(By.XPATH, "./ancestor::*[contains(@class, 'entity-result') or contains(@class, 'search-result')]").text.lower()
                            if not any(x in parent_text for x in ['contacto', 'connection', 'común', 'common', 'mutual']):
                                search_containers.append(link)
                        except:
                            search_containers.append(link)  # Si no puede verificar, incluirlo
            
            print(f"   📊 Total contenedores a procesar: {len(search_containers)}")
            
            profile_links = []
            processed_urls = set()  # Para evitar duplicados
            
            for container in search_containers[:15]:  # Máximo 15
                try:
                    # Buscar enlaces dentro del contenedor
                    links = container.find_elements(By.TAG_NAME, "a") if hasattr(container, 'find_elements') else [container]
                    
                    for link in links:
                        href = link.get_attribute('href')
                        if href and '/in/' in href and href not in processed_urls:
                            # Verificar que sea un perfil válido y no duplicado
                            import re
                            if re.match(r'https://www\.linkedin\.com/in/[^/]+/?(\?.*)?$', href):
                                profile_links.append(link)
                                processed_urls.add(href)
                                break  # Solo un perfil por contenedor
                except:
                    continue
            
            print(f"   🎯 Enlaces de perfil válidos: {len(profile_links)}")
            
            if not profile_links:
                print("   ❌ No se encontraron enlaces de perfil")
                return people_data
            
            # Extraer datos de cada perfil encontrado
            for i, link in enumerate(profile_links[:10]):  # Máximo 10
                try:
                    person_data = {}
                    
                    # URL del perfil (LO MÁS IMPORTANTE)
                    profile_url = link.get_attribute('href')
                    person_data['linkedin_url'] = profile_url
                    
                    # Buscar nombre
                    name = link.text.strip()
                    
                    # Si el enlace no tiene texto, buscar en spans internos
                    if not name or len(name) < 2:
                        spans = link.find_elements(By.TAG_NAME, "span")
                        for span in spans:
                            if span.text.strip() and len(span.text.strip()) > 2:
                                name = span.text.strip()
                                break
                    
                    # Si aún no hay nombre, buscar en elementos aria-hidden
                    if not name or len(name) < 2:
                        try:
                            parent = link.find_element(By.XPATH, "./..")
                            name_spans = parent.find_elements(By.XPATH, ".//span[@aria-hidden='true']")
                            for span in name_spans:
                                text = span.text.strip()
                                if text and len(text) > 2:
                                    # Filtrar textos que no sean nombres
                                    if not any(word in text.lower() for word in ['ver', 'view', 'perfil', 'profile', 'conectar', 'connect']):
                                        name = text
                                        break
                        except:
                            pass
                    
                    if not name:
                        name = f"LinkedIn User {i+1}"
                    
                    person_data['name'] = name
                    
                    # Buscar información adicional en el contenedor
                    try:
                        # Encontrar contenedor principal
                        container = link
                        for _ in range(4):  # Subir máximo 4 niveles
                            try:
                                parent = container.find_element(By.XPATH, "./..")
                                container = parent
                            except:
                                break
                        
                        # Buscar título/cargo con XPath flexible
                        title = ""
                        title_xpaths = [
                            ".//div[contains(@class, 'subtitle') or contains(@class, 'secondary')]",
                            ".//span[contains(@class, 'subtitle') or contains(@class, 'secondary')]",
                            ".//div[contains(text(), 'en ') or contains(text(), 'at ') or contains(text(), 'de ')]"
                        ]
                        
                        for xpath in title_xpaths:
                            try:
                                title_elem = container.find_element(By.XPATH, xpath)
                                if title_elem and title_elem.text.strip():
                                    title = title_elem.text.strip()
                                    break
                            except:
                                continue
                        
                        person_data['title'] = title
                        
                        # Buscar ubicación
                        location = ""
                        location_xpaths = [
                            ".//div[contains(@class, 'location')]",
                            ".//span[contains(text(), ', ')]",
                            ".//div[contains(text(), ', ') and string-length(text()) < 50]"
                        ]
                        
                        for xpath in location_xpaths:
                            try:
                                loc_elem = container.find_element(By.XPATH, xpath)
                                if loc_elem and loc_elem.text.strip():
                                    loc_text = loc_elem.text.strip()
                                    # Verificar que parezca una ubicación
                                    if ',' in loc_text and len(loc_text) < 50:
                                        location = loc_text
                                        break
                            except:
                                continue
                        
                        person_data['location'] = location
                        
                    except Exception as e:
                        person_data['title'] = ""
                        person_data['location'] = ""
                    
                    # Completar datos
                    person_data['description'] = f"{person_data.get('title', '')} | {person_data.get('location', '')}".strip(" |")
                    person_data['source'] = 'LinkedIn'
                    person_data['keyword_used'] = getattr(self, '_current_keyword', '')
                    person_data['industry'] = self.industry.name
                    
                    people_data.append(person_data)
                    
                    print(f"      {i+1}. {name[:40]}")
                    print(f"         🔗 {profile_url}")
                    print(f"         💼 {title[:30]}")
                    print(f"         📍 {location}")
                    
                except Exception as e:
                    print(f"      ❌ Error procesando perfil {i+1}: {e}")
                    continue
        
        except Exception as e:
            print(f"   ❌ Error en extracción robusta: {e}")
        
        print(f"   ✅ Extraídos {len(people_data)} perfiles con URLs")
        return people_data
