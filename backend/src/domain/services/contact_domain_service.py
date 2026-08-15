import re
from typing import List


class ContactDomainService:
    """
    Servicio de dominio para la lógica pura de negocio relacionada con contactos.
    Contiene la lógica de limpieza, validación de formato y de-duplicación de correos.
    """

    _EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

    def clean_emails(self, emails: List[str]) -> List[str]:
        """Normaliza, valida formato y elimina duplicados de una lista de correos."""
        emails = self._normalize(emails)
        emails = self._discard_invalid_format(emails)
        emails = self._discard_duplicates(emails)
        return emails

    def _normalize(self, emails: List[str]) -> List[str]:
        return [email.strip().lower() for email in emails if email and email.strip()]

    def _discard_invalid_format(self, emails: List[str]) -> List[str]:
        return [email for email in emails if self._EMAIL_PATTERN.match(email)]

    def _discard_duplicates(self, emails: List[str]) -> List[str]:
        seen = set()
        unique_emails = []
        for email in emails:
            if email not in seen:
                seen.add(email)
                unique_emails.append(email)
        return unique_emails
