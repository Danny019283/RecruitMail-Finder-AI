import asyncio
from typing import Dict, List, Tuple

from src.application.uses_cases.ports.scraper_port import ScraperPort


class GetSubpagesHtml:
    """
    Caso de Uso: Obtiene el HTML de un conjunto de subpáginas ya filtradas como relevantes,
    descargándolas de forma concurrente y con un límite de concurrencia acotado.
    """
    def __init__(self, scraper: ScraperPort, max_concurrency: int = 5):
        self.scraper = scraper
        self.semaphore = asyncio.Semaphore(max_concurrency)

    async def execute(self, links: List[str]) -> Dict[str, str]:
        if not links:
            return {}

        async def fetch(link: str) -> Tuple[str, str]:
            async with self.semaphore:
                html = await self.scraper.get_html(link)
                return link, html

        results = await asyncio.gather(*(fetch(link) for link in links))
        return {link: html for link, html in results if html}
