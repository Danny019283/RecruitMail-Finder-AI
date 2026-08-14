from datetime import datetime

class Company:
    """
    Entidad de dominio que representa a una empresa en el sistema.
    Contiene la lógica y consistencia interna de los datos de la compañía.
    """
    def __init__(
        self, 
        name: str, 
        domain_url: str, 
        description: str | None = None, 
        id: int | None = None, 
        created_at: datetime | None = None
    ):
        self.__id = id
        # Usamos los setters para validar en la inicialización
        self.name = name
        self.domain_url = domain_url
        self.description = description
        self.__created_at = created_at or datetime.now()

    @property
    def id(self) -> int | None:
        return self.__id

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str):
        if not value or not str(value).strip():
            raise ValueError("El nombre de la empresa no puede estar vacío.")
        self.__name = str(value).strip()

    @property
    def domain_url(self) -> str:
        return self.__domain_url

    @domain_url.setter
    def domain_url(self, value: str):
        if not value or not str(value).strip():
            raise ValueError("El dominio o URL no puede estar vacío.")
        self.__domain_url = str(value).strip().lower()

    @property
    def description(self) -> str | None:
        return self.__description

    @description.setter
    def description(self, value: str | None):
        if value is not None:
            self.__description = str(value).strip()
        else:
            self.__description = None

    @property
    def created_at(self) -> datetime:
        return self.__created_at

    def update_description(self, new_description: str) -> None:
        """
        Lógica de entidad: actualiza la descripción de la empresa.
        """
        self.description = new_description

    def __repr__(self) -> str:
        return f"<Company(id={self.__id}, name='{self.__name}', domain_url='{self.__domain_url}')>"
