from src.domain.entities.contact import Contact
from src.infrastructure.database.models import Contact as ContactModel


class ContactMapper:
    """
    Traduce entre la entidad de dominio Contact y su modelo de persistencia (SQLModel).
    """

    def to_entity(self, model: ContactModel) -> Contact:
        return Contact(
            id=model.id,
            email=model.email,
            id_company=model.id_company,
            subdomain=model.subdomain,
            detected_at=model.detected_at
        )

    def to_model(self, entity: Contact) -> ContactModel:
        return ContactModel(
            id=entity.id,
            email=entity.email,
            id_company=entity.id_company,
            subdomain=entity.subdomain,
            detected_at=entity.detected_at
        )
