from fastapi import APIRouter, Depends, Query
from typing import Optional
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.schemas.deal import DealCreate, DealUpdate, DealResponse
from src.services.deal_service import DealService
from src.dependencies import get_current_user, require_organization, check_organization_access
from src.models.schema import User, DealStatus, DealStage

router = APIRouter(prefix="/api/v1/deals", tags=["Deals"])

@router.get("/", response_model=list[DealResponse])
async def list_deals(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    status: Optional[DealStatus] = Query(None),
    stage: Optional[DealStage] = Query(None),
    min_amount: Optional[Decimal] = Query(None),
    max_amount: Optional[Decimal] = Query(None),
    owner_id: Optional[int] = Query(None),
    order_by: str = Query("created_at"),
    order: str = Query("desc"),
    current_user: User = Depends(get_current_user),
    organization_id: int = Depends(require_organization),
    role: str = Depends(check_organization_access),
    db: AsyncSession = Depends(get_db)
):
    """
    List deals with extensive filtering and pagination.
    Members see only their own deals unless explicitly filtered.
    """
    service = DealService(db)
    return await service.get_deals(
        organization_id=organization_id,
        user=current_user,
        role=role,
        page=page,
        page_size=page_size,
        status=status,
        stage=stage,
        min_amount=min_amount,
        max_amount=max_amount,
        owner_id=owner_id,
        order_by=order_by,
        order=order
    )

@router.post("/", response_model=DealResponse, status_code=201)
async def create_deal(
    data: DealCreate,
    current_user: User = Depends(get_current_user),
    organization_id: int = Depends(require_organization),
    role: str = Depends(check_organization_access),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new deal.
    """
    service = DealService(db)
    return await service.create_deal(
        organization_id=organization_id,
        user=current_user,
        data=data
    )

@router.patch("/{deal_id}", response_model=DealResponse)
async def update_deal(
    deal_id: int,
    data: DealUpdate,
    current_user: User = Depends(get_current_user),
    organization_id: int = Depends(require_organization),
    role: str = Depends(check_organization_access),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a deal. Automatically logs activities for status/stage changes.
    Won deals must have amount > 0.
    Members cannot change stage.
    """
    service = DealService(db)
    return await service.update_deal(
        deal_id=deal_id,
        organization_id=organization_id,
        user=current_user,
        role=role,
        data=data
    )
