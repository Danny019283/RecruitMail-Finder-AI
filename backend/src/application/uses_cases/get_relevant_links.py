from typing import List
from src.application.uses_cases.ports.scraper_port import ScraperPort
from src.application.uses_cases.ports.parser_port import ParserPort
from src.application.uses_cases.ports.link_classify_relenvant_port import LinkClassifierPort
from src.domain.services.company_domain_service import CompanyDomainService

class GetRelevantLinks:
    """
    Caso de Uso: Obtiene una lista de enlaces relevantes de un dominio dado.
    Sigue el flujo de extracción, limpieza y clasificación.
    """
    def __init__(
        self,
        scraper: ScraperPort,
        parser: ParserPort,
        classifier: LinkClassifierPort,
        domain_service: CompanyDomainService
    ):
        self.scraper = scraper
        self.parser = parser
        self.classifier = classifier
        self.domain_service = domain_service

    async def execute(self, domain: str) -> List[str]:
        # 1. Obtener HTML
        html = await self.scraper.get_html(domain)
        if not html:
            return []

        # 2. Parsear HTML
        parsed_dom = self.parser.parse_html(html)

        # 3. Extraer enlaces
        links = self.parser.extract_links(parsed_dom)

        # 4. Limpiar enlaces (lógica pura de dominio delegada al servicio de dominio)
        clean_links = self.domain_service.clean_links(links, domain)

        # 5. Clasificar enlaces relevantes
        if not clean_links:
            return []
        
        relevant_links = await self.classifier.classify_relevant(clean_links)

        return relevant_links
