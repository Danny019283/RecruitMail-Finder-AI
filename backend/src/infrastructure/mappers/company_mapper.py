from src.domain.entities.company import Company
from src.infrastructure.database.models import Company as CompanyModel


class CompanyMapper:
    """
    Traduce entre la entidad de dominio Company y su modelo de persistencia (SQLModel).
    """

    def to_entity(self, model: CompanyModel) -> Company:
        return Company(
            id=model.id,
            name=model.name,
            domain_url=model.domain_url,
            description=model.description,
            created_at=model.created_at
        )

    def to_model(self, entity: Company) -> CompanyModel:
        return CompanyModel(
            id=entity.id,
            name=entity.name,
            domain_url=entity.domain_url,
            description=entity.description,
            created_at=entity.created_at
        )
