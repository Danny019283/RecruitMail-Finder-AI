class ParserPort(Protocol):
    def parse_html(self, html: str) -> Any:
        """Parsea el HTML a una estructura DOM (ej. BeautifulSoup, lxml)."""
        ...
        
    def extract_links(self, parsed_dom: Any) -> List[str]:
        """Extrae todos los enlaces (href) del DOM parseado."""
        ...