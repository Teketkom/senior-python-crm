from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from src.repositories.task import TaskRepository
from src.repositories.deal import DealRepository
from src.repositories.activity import ActivityRepository
from src.schemas.task import TaskCreate, TaskResponse
from src.models.schema import User, ActivityType

class TaskService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.task_repo = TaskRepository(db)
        self.deal_repo = DealRepository(db)
        self.activity_repo = ActivityRepository(db)

    async def get_tasks(
        self,
        organization_id: int,
        user: User,
        role: str,
        deal_id: Optional[int] = None,
        only_open: bool = False,
        due_before: Optional[datetime] = None,
        due_after: Optional[datetime] = None
    ) -> List[TaskResponse]:
        # Validate deal belongs to organization if specified
        if deal_id:
            deal = await self.deal_repo.get_by_id(deal_id)
            if not deal or deal.organization_id != organization_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Deal not found"
                )
            
            # Check member access
            if role == "member" and deal.owner_id != user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this deal"
                )
        
        tasks = await self.task_repo.get_filtered(
            deal_id=deal_id,
            only_open=only_open,
            due_before=due_before,
            due_after=due_after
        )
        
        # Filter by organization membership
        filtered_tasks = []
        for task in tasks:
            deal = await self.deal_repo.get_by_id(task.deal_id)
            if deal and deal.organization_id == organization_id:
                if role == "member" and deal.owner_id != user.id:
                    continue
                filtered_tasks.append(task)
        
        return [TaskResponse.model_validate(t) for t in filtered_tasks]

    async def create_task(
        self,
        organization_id: int,
        user: User,
        role: str,
        data: TaskCreate
    ) -> TaskResponse:
        # Validate deal
        deal = await self.deal_repo.get_by_id(data.deal_id)
        if not deal or deal.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid deal_id"
            )
        
        # Check member permissions
        if role == "member" and deal.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Members can only create tasks for their own deals"
            )
        
        # Validate due_date in future
        if data.due_date and data.due_date < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Due date must be in the future"
            )
        
        task = await self.task_repo.create_task(
            deal_id=data.deal_id,
            title=data.title,
            description=data.description,
            due_date=data.due_date
        )
        
        # Log activity
        await self.activity_repo.create_activity(
            deal_id=data.deal_id,
            activity_type=ActivityType.taskcreated,
            author_id=user.id,
            payload={"task_id": task.id, "title": task.title}
        )
        
        return TaskResponse.model_validate(task)

    async def mark_task_done(
        self,
        task_id: int,
        organization_id: int,
        user: User,
        role: str
    ) -> TaskResponse:
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        deal = await self.deal_repo.get_by_id(task.deal_id)
        if not deal or deal.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        if role == "member" and deal.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        updated_task = await self.task_repo.mark_done(task_id)
        return TaskResponse.model_validate(updated_task)
