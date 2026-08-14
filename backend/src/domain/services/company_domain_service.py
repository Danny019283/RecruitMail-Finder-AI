from typing import List
from urllib.parse import urlparse, urljoin

class CompanyDomainService:
    """
    Servicio de dominio para la lógica pura de negocio relacionada con compañías y sus dominios.
    Contiene la lógica de limpieza y filtrado de enlaces.
    """
    
    def clean_links(self, links: List[str], domain: str) -> List[str]:
        """Limpia, normaliza y filtra enlaces relevantes para el dominio."""
        links = self._discard_anchors(links)
        links = self._discard_mailto(links)
        links = self._discard_javascript(links)
        links = self._normalize_urls(links, domain)
        links = self._discard_outside_domain(links, domain)
        links = self._discard_duplicates(links)
        return links

    def _discard_anchors(self, links: List[str]) -> List[str]:
        return [link for link in links if not link.startswith("#")]

    def _discard_mailto(self, links: List[str]) -> List[str]:
        return [link for link in links if not link.lower().startswith("mailto:")]

    def _discard_javascript(self, links: List[str]) -> List[str]:
        return [link for link in links if not link.lower().startswith("javascript:")]

    def _normalize_urls(self, links: List[str], domain: str) -> List[str]:
        normalized = []
        # Asegurar que el dominio base tenga un esquema para urljoin
        base_url = domain if domain.startswith("http") else f"https://{domain}"
        
        for link in links:
            if link.startswith("/") and not link.startswith("//"):
                normalized.append(urljoin(base_url, link))
            elif not link.startswith("http") and not link.startswith("//"):
                # Rutas relativas como "about.html"
                normalized.append(urljoin(base_url, link))
            elif link.startswith("//"):
                # Rutas relativas al esquema (protocol-relative)
                normalized.append(f"https:{link}")
            else:
                normalized.append(link)
                
        return normalized

    def _discard_outside_domain(self, links: List[str], domain: str) -> List[str]:
        # Obtener el dominio raíz a comparar (sin subdominio www si aplica)
        target_domain = urlparse(domain if domain.startswith("http") else f"https://{domain}").netloc
        if target_domain.startswith("www."):
            target_domain = target_domain[4:]
            
        valid_links = []
        for link in links:
            try:
                link_domain = urlparse(link).netloc
                if link_domain.startswith("www."):
                    link_domain = link_domain[4:]
                
                # Permitir enlaces al mismo dominio exacto o a subdominios de este
                if link_domain == target_domain or link_domain.endswith(f".{target_domain}"):
                    valid_links.append(link)
            except Exception:
                continue
                
        return valid_links

    def _discard_duplicates(self, links: List[str]) -> List[str]:
        # Elimina duplicados conservando el orden de aparición original
        seen = set()
        unique_links = []
        for link in links:
            if link not in seen:
                seen.add(link)
                unique_links.append(link)
        return unique_links
