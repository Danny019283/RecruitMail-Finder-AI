from typing import List, Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.domain.entities.company import Company
from src.infrastructure.database.models import Company as CompanyModel
from src.infrastructure.repository.interfaces.Irepository_company import IRepositoryCompany
from src.infrastructure.mappers.company_mapper import CompanyMapper

class RepositoryCompany(IRepositoryCompany):
    def __init__(self, session: AsyncSession, mapper: Optional[CompanyMapper] = None):
        self.session = session
        self.mapper = mapper or CompanyMapper()

    async def get_by_domain_url(self, domain_url: str) -> Company | None:
        statement = select(CompanyModel).where(CompanyModel.domain_url == domain_url)
        result = (await self.session.exec(statement)).first()
        if result:
            return self.mapper.to_entity(result)
        return None

    async def save(self, company: Company) -> Company:
        model = self.mapper.to_model(company)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self.mapper.to_entity(model)

    async def get_all(self) -> List[Company]:
        statement = select(CompanyModel)
        results = (await self.session.exec(statement)).all()
        return [self.mapper.to_entity(r) for r in results]

    async def get_by_id(self, id_company: int) -> Company | None:
        result = await self.session.get(CompanyModel, id_company)
        if result:
            return self.mapper.to_entity(result)
        return None

    async def update(self, company: Company) -> Company:
        statement = select(CompanyModel).where(CompanyModel.id == company.id)
        result = (await self.session.exec(statement)).first()
        if result:
            result.name = company.name
            result.domain_url = company.domain_url
            result.description = company.description
            self.session.add(result)
            await self.session.commit()
            await self.session.refresh(result)
            return self.mapper.to_entity(result)
        raise ValueError(f"Empresa con id {company.id} no encontrada.")

    async def delete(self, id: int) -> Company | None:
        result = await self.session.get(CompanyModel, id)
        if result:
            entity = self.mapper.to_entity(result)
            await self.session.delete(result)
            await self.session.commit()
            return entity
        return None
