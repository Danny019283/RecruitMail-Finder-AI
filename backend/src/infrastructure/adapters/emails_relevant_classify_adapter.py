from typing import List, Optional

from src.application.uses_cases.ports.email_classify_relevant_port import EmailClassifierPort
from src.infrastructure.ai.openrouter_client import OpenRouterClient
from src.infrastructure.ai.indexed_classifier import classify_indexed

EMAILS_SYSTEM_PROMPT = (
    "Eres un clasificador experto en correos corporativos, usado para obtener correos de "
    "reclutamiento de empresas. Se te da una lista numerada de direcciones de correo "
    "(formato indice|email) encontradas en el sitio web de una empresa. "
    "Tu tarea es identificar cuáles pertenecen a reclutamiento o recursos humanos, guiándote por "
    "términos como los siguientes (o sus variantes evidentes en el prefijo/subdominio del correo):\n\n"
    "English: careers, jobs, hiring, recruitment, recruiting, talent acquisition, human resources, "
    "HR, job openings, vacancies, apply now, join our team, work with us, employment opportunities, "
    "current openings, job board, talent, staffing, onboarding, HR department.\n\n"
    "Español: reclutamiento, contratación, empleo, empleos, vacantes, bolsa de trabajo, talento "
    "humano, recursos humanos, RRHH, únete a nuestro equipo, trabaja con nosotros, postúlate, "
    "oportunidades laborales, ofertas de empleo, selección de personal, gestión de talento, "
    "capital humano, plaza vacante, convocatoria laboral, departamento de RRHH.\n\n"
    "Ignora correos genéricos no ligados a contratación (info@, sales@, support@, contacto@, etc.). "
    "REGLA: descarta siempre los correos nominales (ej. maria.gonzalez@empresa.com, "
    "jperez@empresa.com, o cualquier casilla que identifique a una persona por su nombre propio) "
    "aunque parezcan pertenecer al área de RRHH — un correo nominal nunca se persiste, solo son "
    "válidos los correos genéricos/departamentales de reclutamiento. "
    "Responde únicamente con los índices relevantes en el JSON solicitado."
)


class EmailClassifierAdapter(EmailClassifierPort):
    """
    Implementación del puerto de clasificación de correos (UC-08) usando IA vía OpenRouter.
    """
    def __init__(self, client: Optional[OpenRouterClient] = None):
        self.client = client or OpenRouterClient()

    async def classify_relevant(self, emails: List[str]) -> List[str]:
        return await classify_indexed(
            client=self.client,
            items=emails,
            system_prompt=EMAILS_SYSTEM_PROMPT,
            schema_name="relevant_emails",
        )
