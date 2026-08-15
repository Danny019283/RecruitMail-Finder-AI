import ipaddress
import socket
import httpx
import logging
import re
from typing import Optional
from urllib.parse import urlparse
from enum import Enum
from src.application.uses_cases.ports.scraper_port import ScraperPort

logger = logging.getLogger(__name__)

class PoisonPillType(Enum):
    PAYWALL = 'paywall'
    CAPTCHA = 'captcha'
    RATE_LIMIT = 'rate_limit'
    CLOUDFLARE = 'cloudflare'
    LOGIN_REQUIRED = 'login_required'
    NOT_FOUND = 'not_found'
    NONE = 'none'

def validate_public_url(url: str) -> str:
    """Previene ataques SSRF bloqueando redes locales, credenciales y esquemas inseguros."""
    parsed = urlparse(url)
    if parsed.scheme not in {'http', 'https'}:
        raise ValueError('Only HTTP(S) URLs are allowed')
    if parsed.username or parsed.password or not parsed.hostname:
        raise ValueError('Credentials and missing hosts are not allowed')
    
    port = parsed.port or (443 if parsed.scheme == 'https' else 80)
    try:
        addresses = {
            result[4][0]
            for result in socket.getaddrinfo(parsed.hostname, port)
        }
    except socket.gaierror:
        raise ValueError(f"No se pudo resolver el hostname: {parsed.hostname}")

    if not addresses or any(
        not ipaddress.ip_address(address).is_global for address in addresses
    ):
        raise ValueError('Local and private-network destinations are blocked')
    return url

def detect_poison_pill(url: str, content: str, status_code: int) -> PoisonPillType:
    """Detecta de forma pasiva si la página nos bloqueó o tiene muros de pago/logeo."""
    if status_code == 429: return PoisonPillType.RATE_LIMIT
    if status_code in (401, 403): return PoisonPillType.CLOUDFLARE
    if status_code == 404: return PoisonPillType.NOT_FOUND
    
    patterns = {
        PoisonPillType.CAPTCHA: [r'verify you are human', r'prove you\'re not a robot', r'hcaptcha', r'recaptcha'],
        PoisonPillType.LOGIN_REQUIRED: [r'sign in to continue', r'log in required'],
    }
    content_lower = content.lower()
    for pill_type, type_patterns in patterns.items():
        if any(re.search(p, content_lower) for p in type_patterns):
            return pill_type
    return PoisonPillType.NONE

class ScraperAdapter(ScraperPort):
    """
    Implementación del puerto de scraping que cumple con las pautas éticas
    y validaciones de seguridad de Curriculum Automation.
    """
    def __init__(self, user_agent: str = "CurriculumAutomationBot/1.0 (+https://curriculum-automation.local)"):
        self.user_agent = user_agent

    async def get_html(self, domain: str) -> str:
        # Aseguramos que el input se vuelva una URL válida
        url = domain if domain.startswith("http") else f"https://{domain}"
        
        try:
            # 1. Validación estricta contra SSRF (Server-Side Request Forgery)
            valid_url = validate_public_url(url)
        except ValueError as e:
            logger.error(f"Scraper: URL no válida o insegura ({url}) - {e}")
            return ""

        headers = {
            "User-Agent": self.user_agent
        }

        try:
            # 2. Cliente asíncrono con timeouts sensatos
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                response = await client.get(valid_url, headers=headers)
                
                # 3. Detección de píldoras venenosas (Cloudflare, Captchas, Paywalls)
                pill = detect_poison_pill(valid_url, response.text, response.status_code)
                if pill != PoisonPillType.NONE:
                    logger.warning(f"Scraper: Poison pill tipo '{pill.value}' detectado en {valid_url}. Abortando.")
                    return ""
                
                response.raise_for_status()
                return response.text
                
        except httpx.HTTPError as e:
            logger.error(f"Scraper: Error HTTP accediendo a {url} - {e}")
            return ""
        except Exception as e:
            logger.error(f"Scraper: Error inesperado accediendo a {url} - {e}")
            return ""
