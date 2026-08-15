from abc import ABC, abstractmethod
from src.domain.entities.company import Company
from typing import List, Optional

class IRepositoryCompany(ABC):

    @abstractmethod
    def get_by_domain_url(self, domain_url: str) -> Company | None:
        """UC-02 / UC-03: verifica existencia y retorna la empresa si ya fue analizada."""

    @abstractmethod
    def save(self, company: Company) -> Company:
        """UC-12: persiste una empresa nueva. Retorna la entidad con id asignado."""

    @abstractmethod
    def get_all(self) -> List[Company]:
        """UC-22: catálogo general, sin contactos (join se hace aparte o en el caso de uso)."""

    @abstractmethod
    def get_by_id(self, id_company: int) -> Company | None:
        """Soporte interno para armar relaciones en UC-14."""

    @abstractmethod
    def update(self, company: Company) -> Company:
        """UC-18: actualiza una empresa."""
        
    @abstractmethod
    def delete(self, id: int) -> Company | None:
        """UC-21: elimina una empresa."""