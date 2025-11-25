from typing import List, Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.schema import Activity, ActivityType
from src.repositories.base import BaseRepository

class ActivityRepository(BaseRepository[Activity]):
    def __init__(self, session: AsyncSession):
        super().__init__(Activity, session)

    async def get_by_deal(
        self,
        deal_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Activity]:
        result = await self.session.execute(
            select(Activity)
            .where(Activity.deal_id == deal_id)
            .order_by(Activity.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create_activity(
        self,
        deal_id: int,
        activity_type: ActivityType,
        author_id: Optional[int] = None,
        payload: Optional[Dict[str, Any]] = None
    ) -> Activity:
        activity = Activity(
            deal_id=deal_id,
            author_id=author_id,
            type=activity_type,
            payload=payload
        )
        self.session.add(activity)
        await self.session.commit()
        await self.session.refresh(activity)
        return activity
