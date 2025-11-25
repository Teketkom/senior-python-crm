from typing import List, Optional
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.schema import Contact
from src.repositories.base import BaseRepository

class ContactRepository(BaseRepository[Contact]):
    def __init__(self, session: AsyncSession):
        super().__init__(Contact, session)

    async def get_by_organization(
        self,
        organization_id: int,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        owner_id: Optional[int] = None
    ) -> List[Contact]:
        query = select(Contact).where(Contact.organization_id == organization_id)
        
        if search:
            query = query.where(
                or_(
                    Contact.name.ilike(f"%{search}%"),
                    Contact.email.ilike(f"%{search}%")
                )
            )
        
        if owner_id:
            query = query.where(Contact.owner_id == owner_id)
        
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create_contact(
        self,
        organization_id: int,
        owner_id: int,
        name: str,
        email: Optional[str] = None,
        phone: Optional[str] = None
    ) -> Contact:
        contact = Contact(
            organization_id=organization_id,
            owner_id=owner_id,
            name=name,
            email=email,
            phone=phone
        )
        self.session.add(contact)
        await self.session.commit()
        await self.session.refresh(contact)
        return contact
