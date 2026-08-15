from typing import List

from src.application.uses_cases.ports.scraper_port import ScraperPort
from src.application.uses_cases.ports.parser_port import ParserPort
from src.application.uses_cases.ports.link_classify_relenvant_port import LinkClassifierPort
from src.application.uses_cases.ports.email_classify_relevant_port import EmailClassifierPort
from src.application.uses_cases.get_subpages_html import GetSubpagesHtml
from src.domain.services.company_domain_service import CompanyDomainService
from src.domain.services.contact_domain_service import ContactDomainService


class GetRelevantEmails:
    """
    Caso de Uso: Obtiene los correos de reclutamiento/RRHH relevantes de un dominio dado,
    combinando la página principal y sus subpáginas relevantes (UC-04 a UC-08).
    """
    def __init__(
        self,
        scraper: ScraperPort,
        parser: ParserPort,
        link_classifier: LinkClassifierPort,
        email_classifier: EmailClassifierPort,
        subpages_use_case: GetSubpagesHtml,
        company_domain_service: CompanyDomainService,
        contact_domain_service: ContactDomainService,
    ):
        self.scraper = scraper
        self.parser = parser
        self.link_classifier = link_classifier
        self.email_classifier = email_classifier
        self.subpages_use_case = subpages_use_case
        self.company_domain_service = company_domain_service
        self.contact_domain_service = contact_domain_service

    async def execute(self, domain: str) -> List[str]:
        # 1. Obtener HTML de la página principal (UC-04)
        main_html = await self.scraper.get_html(domain)
        if not main_html:
            return []

        # 2. Derivar los enlaces relevantes (UC-05 + UC-06)
        parsed_dom = self.parser.parse_html(main_html)
        raw_links = self.parser.extract_links(parsed_dom)
        clean_links = self.company_domain_service.clean_links(raw_links, domain)
        relevant_links = (
            await self.link_classifier.classify_relevant(clean_links) if clean_links else []
        )

        # 3. Obtener HTML de las subpáginas relevantes (UC-07)
        subpages_html = await self.subpages_use_case.execute(relevant_links)

        # 4. Extraer correos de la página principal y de las subpáginas
        raw_emails: List[str] = []
        for html in (main_html, *subpages_html.values()):
            raw_emails.extend(self.parser.extract_emails(html))

        # 5. Limpiar y normalizar (lógica pura de dominio)
        clean_emails = self.contact_domain_service.clean_emails(raw_emails)
        if not clean_emails:
            return []

        # 6. Clasificar correos relevantes de reclutamiento/RRHH (UC-08)
        relevant_emails = await self.email_classifier.classify_relevant(clean_emails)

        return relevant_emails
