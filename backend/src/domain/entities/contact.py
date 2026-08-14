import re
from datetime import datetime

class Contact:
    """
    Entidad de dominio que representa a un contacto en el sistema.
    Contiene la lógica y consistencia interna de los datos del contacto.
    """
    def __init__(
        self, 
        email: str,
        id_company: int,
        subdomain: str,
        id: int | None = None, 
        detected_at: datetime | None = None
    ):
        self.__id = id
        self.id_company = id_company
        self.subdomain = subdomain
        # Usamos el setter para validar en la inicialización
        self.email = email
        self.__detected_at = detected_at or datetime.now()

    @property
    def id(self) -> int | None:
        return self.__id

    @property
    def id_company(self) -> int:
        return self.__id_company

    @id_company.setter
    def id_company(self, value: int):
        if not value or value <= 0:
            raise ValueError("El id_company no es válido.")
        self.__id_company = value

    @property
    def subdomain(self) -> str:
        return self.__subdomain

    @subdomain.setter
    def subdomain(self, value: str):
        if not value or not str(value).strip():
            raise ValueError("El subdominio no puede estar vacío.")
        self.__subdomain = str(value).strip().lower()

    @property
    def email(self) -> str:
        return self.__email

    @email.setter
    def email(self, value: str):
        if not value or not str(value).strip():
            raise ValueError("El email no puede estar vacío.")
        
        email_clean = str(value).strip().lower()
        # Validación básica de formato de email
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email_clean):
            raise ValueError(f"El email '{email_clean}' no tiene un formato válido.")
            
        self.__email = email_clean

    @property
    def detected_at(self) -> datetime:
        return self.__detected_at

    def __repr__(self) -> str:
        return f"<Contact(id={self.__id}, email='{self.__email}', id_company={self.__id_company}, subdomain='{self.__subdomain}')>"
