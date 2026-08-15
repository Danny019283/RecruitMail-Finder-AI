from typing import List, Protocol


class EmailClassifierPort(Protocol):
    async def classify_relevant(self, emails: List[str]) -> List[str]:
        """Filtra y retorna solo los correos relevantes de reclutamiento/RRHH (ej. mediante IA)."""
        ...
