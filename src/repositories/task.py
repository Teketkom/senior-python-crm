from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.schema import Task
from src.repositories.base import BaseRepository

class TaskRepository(BaseRepository[Task]):
    def __init__(self, session: AsyncSession):
        super().__init__(Task, session)

    async def get_by_deal(
        self,
        deal_id: int,
        only_open: bool = False
    ) -> List[Task]:
        query = select(Task).where(Task.deal_id == deal_id)
        
        if only_open:
            query = query.where(Task.is_done == False)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_filtered(
        self,
        deal_id: Optional[int] = None,
        only_open: bool = False,
        due_before: Optional[datetime] = None,
        due_after: Optional[datetime] = None
    ) -> List[Task]:
        query = select(Task)
        
        conditions = []
        if deal_id:
            conditions.append(Task.deal_id == deal_id)
        if only_open:
            conditions.append(Task.is_done == False)
        if due_before:
            conditions.append(Task.due_date <= due_before)
        if due_after:
            conditions.append(Task.due_date >= due_after)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create_task(
        self,
        deal_id: int,
        title: str,
        description: Optional[str] = None,
        due_date: Optional[datetime] = None
    ) -> Task:
        task = Task(
            deal_id=deal_id,
            title=title,
            description=description,
            due_date=due_date,
            is_done=False
        )
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def mark_done(self, task_id: int) -> Optional[Task]:
        task = await self.get_by_id(task_id)
        if task:
            task.is_done = True
            await self.session.commit()
            await self.session.refresh(task)
        return task
