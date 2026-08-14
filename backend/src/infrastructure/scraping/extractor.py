import re
from typing import List, Set, Optional
from bs4 import BeautifulSoup
from urllib.parse import urlparse


class Extractor:
    """
    Parser that extracts specific structured data (internal links and emails) from raw HTML.
    Uses a clean, Pythonic architecture with single-responsibility methods.
    """

    def __init__(self):
        self._email_pattern = re.compile(
            r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        )
        # Tags that don't contain readable text
        self._ignored_tags = {"script", "style", "noscript", "meta", "svg"}

    def extract_emails(self, html_content: str) -> List[str]:
        """
        Parses HTML and extracts valid email addresses from text and 'mailto' links.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        raw_text = self._clean_html_to_text(soup)
        
        emails = set(self._email_pattern.findall(raw_text))
        emails.update(self._extract_emails_from_links(soup))
        
        return sorted(list(emails))

    def extract_links(self, html_content: str, base_url: str = "") -> List[str]:
        """
        Parses HTML and extracts valid internal links.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        links = set()
        base_domain = urlparse(base_url).netloc if base_url else ""
        
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"].strip()
            
            if not self._is_valid_link(href):
                continue
                
            internal_path = self._get_internal_path(href, base_domain)
            if internal_path:
                links.add(internal_path)
                
        return sorted(list(links))

    def _clean_html_to_text(self, soup: BeautifulSoup) -> str:
        """
        Strips unnecessary tags and extracts clean readable text.
        """
        visible_texts = [
            text.strip()
            for text in soup.find_all(string=True)
            if text.parent.name not in self._ignored_tags and text.strip()
        ]
        clean_text = " ".join(visible_texts)
        # Collapse multiple spaces
        return re.sub(r"\s+", " ", clean_text)

    def _extract_emails_from_links(self, soup: BeautifulSoup) -> Set[str]:
        """
        Finds and validates emails strictly inside 'mailto:' anchor tags.
        """
        emails = set()
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"].lower()
            if href.startswith("mailto:"):
                # Use Python 3.9+ removeprefix
                email = href.removeprefix("mailto:").split("?")[0].strip()
                if self._email_pattern.match(email):
                    emails.add(email)
        return emails

    def _is_valid_link(self, href: str) -> bool:
        """
        Checks if an href is a standard web link, ignoring anchors and scripts.
        """
        invalid_prefixes = ("#", "javascript:", "tel:", "mailto:")
        return bool(href and not href.startswith(invalid_prefixes))

    def _get_internal_path(self, href: str, base_domain: str) -> Optional[str]:
        """
        Evaluates if a link is internal and returns its path, or None if external.
        """
        parsed = urlparse(href)
        
        # Relative link
        if not parsed.netloc:
            return href
            
        # Absolute link but pointing to the same domain
        if base_domain and parsed.netloc == base_domain:
            return parsed.path or "/"
            
        return None
