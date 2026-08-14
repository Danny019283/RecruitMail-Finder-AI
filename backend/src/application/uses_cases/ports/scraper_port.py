class ScraperPort(Protocol):
    async def get_html(self, domain: str) -> str:
        """Obtiene el HTML crudo del dominio especificado."""
        ...
