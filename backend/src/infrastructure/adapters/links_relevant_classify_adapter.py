from typing import List, Optional

from src.application.uses_cases.ports.link_classify_relenvant_port import LinkClassifierPort
from src.infrastructure.ai.openrouter_client import OpenRouterClient
from src.infrastructure.ai.indexed_classifier import classify_indexed

LINKS_SYSTEM_PROMPT = (
    "Eres un clasificador experto en sitios web corporativos, usado para obtener enlaces de "
    "reclutamiento de empresas. Se te da una lista numerada de URLs (formato indice|url) "
    "encontradas en el sitio web de una empresa. Tu tarea es identificar cuáles apuntan a "
    "páginas de reclutamiento, empleo, carreras o recursos humanos, guiándote por términos "
    "como los siguientes (o sus variantes evidentes en la ruta/slug de la URL):\n\n"
    "English: careers, jobs, hiring, recruitment, recruiting, talent acquisition, human resources, "
    "HR, job openings, vacancies, apply now, join our team, work with us, employment opportunities, "
    "current openings, job board, talent, staffing, onboarding, HR department.\n\n"
    "Español: reclutamiento, contratación, empleo, empleos, vacantes, bolsa de trabajo, talento "
    "humano, recursos humanos, RRHH, únete a nuestro equipo, trabaja con nosotros, postúlate, "
    "oportunidades laborales, ofertas de empleo, selección de personal, gestión de talento, "
    "capital humano, plaza vacante, convocatoria laboral, departamento de RRHH.\n\n"
    "Ignora cualquier otra página no ligada a reclutamiento (productos, blog, contacto general, "
    "legal, prensa, etc.). "
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
