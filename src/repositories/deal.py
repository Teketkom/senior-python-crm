from typing import List, Optional
from decimal import Decimal
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.schema import Deal, DealStatus, DealStage
from src.repositories.base import BaseRepository

class DealRepository(BaseRepository[Deal]):
    def __init__(self, session: AsyncSession):
        super().__init__(Deal, session)

    async def get_by_organization(
        self,
        organization_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[DealStatus] = None,
        stage: Optional[DealStage] = None,
        min_amount: Optional[Decimal] = None,
        max_amount: Optional[Decimal] = None,
        owner_id: Optional[int] = None,
        order_by: str = "created_at",
        order: str = "desc"
    ) -> List[Deal]:
        query = select(Deal).where(Deal.organization_id == organization_id)
        
        if status:
            query = query.where(Deal.status == status)
        
        if stage:
            query = query.where(Deal.stage == stage)
        
        if min_amount is not None:
            query = query.where(Deal.amount >= min_amount)
        
        if max_amount is not None:
            query = query.where(Deal.amount <= max_amount)
        
        if owner_id:
            query = query.where(Deal.owner_id == owner_id)
        
        if order_by == "amount":
            order_col = Deal.amount
        else:
            order_col = Deal.created_at
        
        if order == "asc":
            query = query.order_by(order_col.asc())
        else:
            query = query.order_by(order_col.desc())
        
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create_deal(
        self,
        organization_id: int,
        owner_id: int,
        title: str,
        amount: Decimal,
        currency: str,
        contact_id: Optional[int] = None,
        status: DealStatus = DealStatus.new,
        stage: DealStage = DealStage.qualification
    ) -> Deal:
        deal = Deal(
            organization_id=organization_id,
            owner_id=owner_id,
            title=title,
            amount=amount,
            currency=currency,
            contact_id=contact_id,
            status=status,
            stage=stage
        )
        self.session.add(deal)
        await self.session.commit()
        await self.session.refresh(deal)
        return deal
