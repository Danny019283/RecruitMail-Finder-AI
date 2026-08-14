from typing import List
from sqlmodel import Session, select
from src.domain.entities.contact import Contact
from src.infrastructure.database.models import Contact as ContactModel
from src.infrastructure.repository.interfaces.Irepository_contact import IRepositoryContact

class RepositoryContact(IRepositoryContact):
    def __init__(self, session: Session):
        self.session = session

    def _to_entity(self, model: ContactModel) -> Contact:
        return Contact(
            id=model.id,
            email=model.email,
            id_company=model.id_company,
            subdomain=model.subdomain,
            detected_at=model.detected_at
        )

    def _to_model(self, entity: Contact) -> ContactModel:
        return ContactModel(
            id=entity.id,
            email=entity.email,
            id_company=entity.id_company,
            subdomain=entity.subdomain,
            detected_at=entity.detected_at
        )

    def get_by_email(self, email: str) -> Contact | None:
        statement = select(ContactModel).where(ContactModel.email == email)
        result = self.session.exec(statement).first()
        if result:
            return self._to_entity(result)
        return None

    def save(self, contact: Contact) -> Contact:
        model = self._to_model(contact)
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    def get_all(self) -> List[Contact]:
        statement = select(ContactModel)
        results = self.session.exec(statement).all()
        return [self._to_entity(r) for r in results]

    def get_by_id(self, id_contact: int) -> Contact | None:
        result = self.session.get(ContactModel, id_contact)
        if result:
            return self._to_entity(result)
        return None

    def update(self, contact: Contact) -> Contact:
        statement = select(ContactModel).where(ContactModel.id == contact.id)
        result = self.session.exec(statement).first()
        if result:
            result.email = contact.email
            result.id_company = contact.id_company
            result.subdomain = contact.subdomain
            self.session.add(result)
            self.session.commit()
            self.session.refresh(result)
            return self._to_entity(result)
        raise ValueError(f"Contacto con id {contact.id} no encontrado.")

    def delete(self, id: int) -> Contact | None:
        result = self.session.get(ContactModel, id)
        if result:
            entity = self._to_entity(result)
            self.session.delete(result)
            self.session.commit()
            return entity
        return None
