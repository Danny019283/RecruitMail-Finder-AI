from abc import ABC, abstractmethod
from src.domain.entities import CompanyContact
from typing import List, Optional


class IRepositoryCompanyContact(ABC):

    @abstractmethod
    def exists_relation(self, id_company: int, id_contact: int, subdomain: str) -> bool:
        """UC-14: evita duplicar la misma tripleta si se re-analiza (complementa el
        UNIQUE(id_company, id_contact, subdomain) de DB, para no depender solo de
        capturar la excepción de integridad)."""

    @abstractmethod
    def save(self, company_contact: CompanyContact) -> CompanyContact:
        """UC-14: crea la relación empresa-contacto-subdominio."""

    @abstractmethod
    def get_by_company(self, id_company: int) -> List[CompanyContact]:
        """UC-20 / UC-21: trae todas las relaciones (con su contacto y subdominio)
        para mostrar en el front y exportar a CSV."""

    @abstractmethod
    def get_all_with_company(self) -> List[CompanyContact]:
        """UC-22: catálogo general — trae todo con join a empresa y contacto para
        pintar la tabla completa nombre_empresa + email."""

    @abstractmethod
    def get_by_id(self, id: int) -> CompanyContact | None:
        """Soporte interno / utilitario."""

    @abstractmethod
    def delete(self, id: int) -> CompanyContact | None:
        """Elimina una relación puntual sin afectar el Contact ni el Company base."""