import httpx
from typing import Optional
import socket
import ipaddress
from urllib.parse import urlparse
from enum import Enum
import re


class ScraperError(Exception):
    """Base exception for Scraper errors."""
    pass


class AccessDeniedError(ScraperError):
    """The origin denied automated access (Poison Pill detected)."""
    pass


class PoisonPillType(Enum):
    PAYWALL = 'paywall'
    CAPTCHA = 'captcha'
    RATE_LIMIT = 'rate_limit'
    CLOUDFLARE = 'cloudflare'
    LOGIN_REQUIRED = 'login_required'
    NOT_FOUND = 'not_found'
    NONE = 'none'


def validate_public_url(url: str) -> str:
    """Validates that a URL is public and protects against SSRF."""
    parsed = urlparse(url)
    if parsed.scheme not in {'http', 'https'}:
        raise ValueError('Only HTTP(S) URLs are allowed')
    if parsed.username or parsed.password or not parsed.hostname:
        raise ValueError('Credentials and missing hosts are not allowed')
    
    port = parsed.port or (443 if parsed.scheme == 'https' else 80)
    addresses = {
        result[4][0]
        for result in socket.getaddrinfo(parsed.hostname, port)
    }
    if not addresses or any(
        not ipaddress.ip_address(address).is_global for address in addresses
    ):
        raise ValueError('Local and private-network destinations are blocked')
    return url


def detect_poison_pill(url: str, content: str, status_code: int) -> PoisonPillType:
    """Detects if the page is blocking the scraper or requesting authentication."""
    if status_code == 429: return PoisonPillType.RATE_LIMIT
    if status_code in (401, 403): return PoisonPillType.CLOUDFLARE
    if status_code == 404: return PoisonPillType.NOT_FOUND
    
    patterns = {
        PoisonPillType.CAPTCHA: [r'verify you are human', r'prove you\'re not a robot', r'captcha'],
        PoisonPillType.LOGIN_REQUIRED: [r'sign in to continue', r'log in required', r'create an account'],
        PoisonPillType.PAYWALL: [r'subscribe to continue', r'subscription required', r'become a member']
    }
    content_lower = content.lower()
    for pill_type, type_patterns in patterns.items():
        if any(re.search(p, content_lower) for p in type_patterns):
            return pill_type
    return PoisonPillType.NONE


class Scraper:
    """
    A simple web scraper that focuses solely on retrieving HTML content.
    It handles HTTP requests, errors, timeouts, redirects, and validates content types.
    """

    def __init__(self, timeout: float = 10.0, max_redirects: int = 5):
        self.timeout = timeout
        self.max_redirects = max_redirects
        # Use a descriptive User-Agent as per web-scraping guidelines
        self.headers = {
            "User-Agent": "CurriculumAutomationScraper/1.0 (+https://your-domain.com/bot)"
        }

    async def obtener(self, url: str) -> str:
        """
        Fetches the HTML content from the given URL.
        
        Args:
            url (str): The URL to scrape.
            
        Returns:
            str: The HTML content of the page.
            
        Raises:
            ScraperError: If the request fails, times out, or returns non-HTML.
        """
        try:
            # Untrusted content boundary validation
            url = validate_public_url(url)
            
            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
                max_redirects=self.max_redirects,
                headers=self.headers
            ) as client:
                response = await client.get(url)
                
                # Check for Poison Pills BEFORE raising for status,
                # to gracefully handle 401/403/429
                pill = detect_poison_pill(url, response.text, response.status_code)
                if pill != PoisonPillType.NONE:
                    raise AccessDeniedError(
                        f"Scraping blocked: Detected poison pill '{pill.value}' at {url}"
                    )
                
                # Handle HTTP errors (4xx, 5xx) that aren't poison pills
                response.raise_for_status()
                
                # Identify if the response is HTML
                content_type = response.headers.get("Content-Type", "")
                if "text/html" not in content_type.lower():
                    raise ScraperError(
                        f"Expected HTML response, but got Content-Type: '{content_type}' "
                        f"for URL: {url}"
                    )
                
                # Return the HTML content
                return response.text
                
        except httpx.TimeoutException:
            raise ScraperError(
                f"Timeout of {self.timeout}s exceeded for URL: {url}"
            )
        except httpx.TooManyRedirects:
            raise ScraperError(
                f"Exceeded max redirects ({self.max_redirects}) for URL: {url}"
            )
        except httpx.HTTPStatusError as e:
            raise ScraperError(
                f"HTTP Error {e.response.status_code} when requesting {url}"
            )
        except httpx.RequestError as e:
            raise ScraperError(
                f"Network error while connecting to {url}: {e}"
            )
