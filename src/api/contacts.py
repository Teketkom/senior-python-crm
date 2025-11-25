from fastapi import APIRouter, Depends, Query
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.schemas.contact import ContactCreate, ContactResponse
from src.services.contact_service import ContactService
from src.dependencies import get_current_user, require_organization, check_organization_access
from src.models.schema import User

router = APIRouter(prefix="/api/v1/contacts", tags=["Contacts"])

@router.get("/", response_model=list[ContactResponse])
async def list_contacts(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    owner_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    organization_id: int = Depends(require_organization),
    role: str = Depends(check_organization_access),
    db: AsyncSession = Depends(get_db)
):
    """
    List contacts with filtering and pagination.
    Members see only their own contacts unless explicitly filtered.
    """
    service = ContactService(db)
    return await service.get_contacts(
        organization_id=organization_id,
        user=current_user,
        role=role,
        page=page,
        page_size=page_size,
        search=search,
        owner_id=owner_id
    )

@router.post("/", response_model=ContactResponse, status_code=201)
async def create_contact(
    data: ContactCreate,
    current_user: User = Depends(get_current_user),
    organization_id: int = Depends(require_organization),
    role: str = Depends(check_organization_access),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new contact in the organization.
    """
    service = ContactService(db)
    return await service.create_contact(
        organization_id=organization_id,
        user=current_user,
        data=data
    )
