from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class CompanyContact(SQLModel, table=True):
    __tablename__ = "company_contact"
    __table_args__ = (
        UniqueConstraint("id_company", "id_contact", "subdomain", name="uix_company_contact_subdomain"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    id_company: int = Field(foreign_key="company.id", nullable=False)
    id_contact: int = Field(foreign_key="contact.id", nullable=False)
    subdomain: str = Field(max_length=255, nullable=False)

    # Relationships
    company: "Company" = Relationship(back_populates="company_contacts")
    contact: "Contact" = Relationship(back_populates="company_contacts")

class Company(SQLModel, table=True):
    __tablename__ = "company"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255, nullable=False)
    domain_url: str = Field(max_length=255, nullable=False, unique=True, index=True)
    description: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=utc_now, nullable=False)

    # Relationships
    company_contacts: List[CompanyContact] = Relationship(back_populates="company", cascade_delete=True)

class Contact(SQLModel, table=True):
    __tablename__ = "contact"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(max_length=255, nullable=False, unique=True, index=True)
    detected_at: datetime = Field(default_factory=utc_now, nullable=False)

    # Relationships
    company_contacts: List[CompanyContact] = Relationship(back_populates="contact", cascade_delete=True)
