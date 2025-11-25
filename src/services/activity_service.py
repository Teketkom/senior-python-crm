from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from src.repositories.activity import ActivityRepository
from src.repositories.deal import DealRepository
from src.schemas.activity import ActivityCreate, ActivityResponse
from src.models.schema import User, ActivityType

class ActivityService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.activity_repo = ActivityRepository(db)
        self.deal_repo = DealRepository(db)

    async def get_activities(
        self,
        deal_id: int,
        organization_id: int,
        user: User,
        role: str,
        page: int = 1,
        page_size: int = 50
    ) -> List[ActivityResponse]:
        deal = await self.deal_repo.get_by_id(deal_id)
        if not deal or deal.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deal not found"
            )
        
        if role == "member" and deal.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        skip = (page - 1) * page_size
        activities = await self.activity_repo.get_by_deal(
            deal_id=deal_id,
            skip=skip,
            limit=page_size
        )
        
        return [ActivityResponse.model_validate(a) for a in activities]

    async def create_activity(
        self,
        deal_id: int,
        organization_id: int,
        user: User,
        role: str,
        data: ActivityCreate
    ) -> ActivityResponse:
        # Only allow comment type via API
        if data.type != ActivityType.comment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only 'comment' type activities can be created via this endpoint"
            )
        
        deal = await self.deal_repo.get_by_id(deal_id)
        if not deal or deal.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deal not found"
            )
        
        if role == "member" and deal.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        activity = await self.activity_repo.create_activity(
            deal_id=deal_id,
            activity_type=data.type,
            author_id=user.id,
            payload=data.payload
        )
        
        return ActivityResponse.model_validate(activity)
