class LinkClassifierPort(Protocol):
    async def classify_relevant(self, links: List[str]) -> List[str]:
        """Filtra y retorna solo los enlaces relevantes (ej. mediante IA o reglas)."""
        ...