from typing import List, Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.domain.entities.contact import Contact
from src.infrastructure.database.models import Contact as ContactModel
from src.infrastructure.repository.interfaces.Irepository_contact import IRepositoryContact
from src.infrastructure.mappers.contact_mapper import ContactMapper

class RepositoryContact(IRepositoryContact):
    def __init__(self, session: AsyncSession, mapper: Optional[ContactMapper] = None):
        self.session = session
        self.mapper = mapper or ContactMapper()

    async def get_by_email(self, email: str) -> Contact | None:
        statement = select(ContactModel).where(ContactModel.email == email)
        result = (await self.session.exec(statement)).first()
        if result:
            return self.mapper.to_entity(result)
        return None

    async def save(self, contact: Contact) -> Contact:
        model = self.mapper.to_model(contact)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self.mapper.to_entity(model)

    async def get_all(self) -> List[Contact]:
        statement = select(ContactModel)
        results = (await self.session.exec(statement)).all()
        return [self.mapper.to_entity(r) for r in results]

    async def get_by_id(self, id_contact: int) -> Contact | None:
        result = await self.session.get(ContactModel, id_contact)
        if result:
            return self.mapper.to_entity(result)
        return None

    async def update(self, contact: Contact) -> Contact:
        statement = select(ContactModel).where(ContactModel.id == contact.id)
        result = (await self.session.exec(statement)).first()
        if result:
            result.email = contact.email
            result.id_company = contact.id_company
            result.subdomain = contact.subdomain
            self.session.add(result)
            await self.session.commit()
            await self.session.refresh(result)
            return self.mapper.to_entity(result)
        raise ValueError(f"Contacto con id {contact.id} no encontrado.")

    async def delete(self, id: int) -> Contact | None:
        result = await self.session.get(ContactModel, id)
        if result:
            entity = self.mapper.to_entity(result)
            await self.session.delete(result)
            await self.session.commit()
            return entity
        return None
