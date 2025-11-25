from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from src.repositories.contact import ContactRepository
from src.schemas.contact import ContactCreate, ContactResponse
from src.models.schema import User

class ContactService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.contact_repo = ContactRepository(db)

    async def get_contacts(
        self,
        organization_id: int,
        user: User,
        role: str,
        page: int = 1,
        page_size: int = 50,
        search: Optional[str] = None,
        owner_id: Optional[int] = None
    ) -> List[ContactResponse]:
        # Role-based filtering
        if role == "member" and owner_id is None:
            owner_id = user.id
        elif role in ["manager", "admin", "owner"] and owner_id:
            # Can filter by specific owner
            pass
        
        skip = (page - 1) * page_size
        contacts = await self.contact_repo.get_by_organization(
            organization_id=organization_id,
            skip=skip,
            limit=page_size,
            search=search,
            owner_id=owner_id
        )
        
        return [ContactResponse.model_validate(c) for c in contacts]

    async def create_contact(
        self,
        organization_id: int,
        user: User,
        data: ContactCreate
    ) -> ContactResponse:
        contact = await self.contact_repo.create_contact(
            organization_id=organization_id,
            owner_id=user.id,
            name=data.name,
            email=data.email,
            phone=data.phone
        )
        return ContactResponse.model_validate(contact)
