from abc import ABC, abstractmethod
from src.domain.entities.contact import Contact
from typing import List, Optional


class IRepositoryContact(ABC):

    @abstractmethod
    def get_by_email(self, email: str) -> Contact | None:
        """UC-11: valida si el correo genérico ya existe globalmente antes de insertar."""

    @abstractmethod
    def save(self, contact: Contact) -> Contact:
        """UC-13: persiste un contacto nuevo. Solo se llama si get_by_email() retornó None."""

    @abstractmethod
    def get_all(self) -> List[Contact]:
        """Soporte interno / utilitario, no ligado a un UC directo aún."""

    @abstractmethod
    def get_by_id(self, id_contact: int) -> Contact | None:
        """Soporte interno para armar relaciones en UC-14."""

    @abstractmethod
    def update(self, contact: Contact) -> Contact:
        """Actualiza un contacto (ej: corrección manual de un email mal capturado)."""

    @abstractmethod
    def delete(self, id: int) -> Contact | None:
        """Elimina un contacto. OJO: revisar en el caso de uso si primero hay que
        eliminar en cascada las filas de company_contact asociadas, o si la FK
        ya lo maneja a nivel de DB."""