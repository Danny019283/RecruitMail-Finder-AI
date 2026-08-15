from typing import List, Optional

from src.application.uses_cases.ports.link_classify_relenvant_port import LinkClassifierPort
from src.infrastructure.ai.openrouter_client import OpenRouterClient
from src.infrastructure.ai.indexed_classifier import classify_indexed

LINKS_SYSTEM_PROMPT = (
    "Eres un clasificador experto en sitios web corporativos. Se te da una lista numerada de "
    "URLs (formato indice|url) encontradas en el dominio de una empresa. Tu tarea es identificar "
    "cuáles apuntan a páginas de reclutamiento, empleo, carreras o recursos humanos "
    "(ej. /careers, /jobs, /trabaja-con-nosotros, /empleo, /rrhh, /join-us, /talent, /vacantes). "
    "Ignora cualquier otra página (productos, blog, contacto general, legal, prensa, etc.). "
    "Responde únicamente con los índices relevantes en el JSON solicitado."
)


class LinkClassifierAdapter(LinkClassifierPort):
    """
    Implementación del puerto de clasificación de enlaces (UC-06) usando IA vía OpenRouter.
    """
    def __init__(self, client: Optional[OpenRouterClient] = None):
        self.client = client or OpenRouterClient()

    async def classify_relevant(self, links: List[str]) -> List[str]:
        return await classify_indexed(
            client=self.client,
            items=links,
            system_prompt=LINKS_SYSTEM_PROMPT,
            schema_name="relevant_links",
        )
