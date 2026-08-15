import re
from typing import Any, List
from bs4 import BeautifulSoup
from src.application.uses_cases.ports.parser_port import ParserPort

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")

class ParserAdapter(ParserPort):
    """
    Implementación del puerto de parsing utilizando BeautifulSoup.
    Responsable de convertir HTML en crudo en un DOM navegable y de extraer datos.
    """
    def parse_html(self, html: str) -> Any:
        # Usamos html.parser (viene nativo en Python, o se puede cambiar a lxml si está disponible)
        return BeautifulSoup(html, "html.parser")

    def extract_links(self, parsed_dom: Any) -> List[str]:
        if not isinstance(parsed_dom, BeautifulSoup):
            raise ValueError("El DOM parseado debe ser un objeto de BeautifulSoup")

        links = []
        for a_tag in parsed_dom.find_all("a", href=True):
            links.append(a_tag["href"])
        return links

    def extract_emails(self, html: str) -> List[str]:
        soup = self.parse_html(html)
        emails: List[str] = []

        # 1. Correos declarados explícitamente como enlaces mailto:
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            if href.lower().startswith("mailto:"):
                address = href.split(":", 1)[1].split("?", 1)[0].strip()
                if address:
                    emails.append(address)

        # 2. Correos escritos como texto plano en la página
        emails.extend(EMAIL_REGEX.findall(soup.get_text(" ")))

        return emails
