from typing import Any, List, Protocol


class ParserPort(Protocol):
    def parse_html(self, html: str) -> Any:
        """Parsea el HTML a una estructura DOM (ej. BeautifulSoup, lxml)."""
        ...
        
    def extract_links(self, parsed_dom: Any) -> List[str]:
        """Extrae todos los enlaces (href) del DOM parseado."""
        ...

    def extract_emails(self, html: str) -> List[str]:
        """Extrae correos electrónicos del HTML crudo (mailto: hrefs y texto plano)."""
        ...