from typing import List, Optional
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from src.repositories.deal import DealRepository
from src.repositories.contact import ContactRepository
from src.repositories.activity import ActivityRepository
from src.schemas.deal import DealCreate, DealUpdate, DealResponse
from src.models.schema import User, DealStatus, DealStage, ActivityType

class DealService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.deal_repo = DealRepository(db)
        self.contact_repo = ContactRepository(db)
        self.activity_repo = ActivityRepository(db)

    async def get_deals(
        self,
        organization_id: int,
        user: User,
        role: str,
        page: int = 1,
        page_size: int = 50,
        status: Optional[DealStatus] = None,
        stage: Optional[DealStage] = None,
        min_amount: Optional[Decimal] = None,
        max_amount: Optional[Decimal] = None,
        owner_id: Optional[int] = None,
        order_by: str = "created_at",
        order: str = "desc"
    ) -> List[DealResponse]:
        # Role-based filtering
        if role == "member" and owner_id is None:
            owner_id = user.id
        
        skip = (page - 1) * page_size
        deals = await self.deal_repo.get_by_organization(
            organization_id=organization_id,
            skip=skip,
            limit=page_size,
            status=status,
            stage=stage,
            min_amount=min_amount,
            max_amount=max_amount,
            owner_id=owner_id,
            order_by=order_by,
            order=order
        )
        
        return [DealResponse.model_validate(d) for d in deals]

    async def create_deal(
        self,
        organization_id: int,
        user: User,
        data: DealCreate
    ) -> DealResponse:
        # Validate contact belongs to organization if provided
        if data.contact_id:
            contact = await self.contact_repo.get_by_id(data.contact_id)
            if not contact or contact.organization_id != organization_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid contact_id for this organization"
                )
        
        deal = await self.deal_repo.create_deal(
            organization_id=organization_id,
            owner_id=user.id,
            title=data.title,
            amount=data.amount,
            currency=data.currency,
            contact_id=data.contact_id
        )
        
        return DealResponse.model_validate(deal)

    async def update_deal(
        self,
        deal_id: int,
        organization_id: int,
        user: User,
        role: str,
        data: DealUpdate
    ) -> DealResponse:
        deal = await self.deal_repo.get_by_id(deal_id)
        
        if not deal or deal.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deal not found"
            )
        
        # Check permissions
        if role == "member" and deal.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Members can only modify their own deals"
            )
        
        # Validate won status has amount > 0
        if data.status == DealStatus.won:
            final_amount = data.amount if data.amount is not None else deal.amount
            if final_amount <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Won deals must have amount > 0"
                )
        
        # Check stage permission for members
        if data.stage and role == "member":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Members cannot change deal stage"
            )
        
        # Track status/stage changes
        old_status = deal.status
        old_stage = deal.stage
        
        # Update deal
        update_data = data.model_dump(exclude_unset=True)
        updated_deal = await self.deal_repo.update(deal_id, **update_data)
        
        # Log activities
        if data.status and data.status != old_status:
            await self.activity_repo.create_activity(
                deal_id=deal_id,
                activity_type=ActivityType.statuschanged,
                author_id=user.id,
                payload={"from": old_status.value, "to": data.status.value}
            )
        
        if data.stage and data.stage != old_stage:
            await self.activity_repo.create_activity(
                deal_id=deal_id,
                activity_type=ActivityType.system,
                author_id=user.id,
                payload={"action": "stage_changed", "from": old_stage.value, "to": data.stage.value}
            )
        
        return DealResponse.model_validate(updated_deal)
