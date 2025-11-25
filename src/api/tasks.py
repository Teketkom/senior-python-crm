from fastapi import APIRouter, Depends, Query
from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.schemas.task import TaskCreate, TaskResponse
from src.services.task_service import TaskService
from src.dependencies import get_current_user, require_organization, check_organization_access
from src.models.schema import User

router = APIRouter(prefix="/api/v1/tasks", tags=["Tasks"])

@router.get("/", response_model=list[TaskResponse])
async def list_tasks(
    deal_id: Optional[int] = Query(None),
    only_open: bool = Query(False),
    due_before: Optional[datetime] = Query(None),
    due_after: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
    organization_id: int = Depends(require_organization),
    role: str = Depends(check_organization_access),
    db: AsyncSession = Depends(get_db)
):
    """
    List tasks with filtering by deal, completion status, and due dates.
    Members can only see tasks for their own deals.
    """
    service = TaskService(db)
    return await service.get_tasks(
        organization_id=organization_id,
        user=current_user,
        role=role,
        deal_id=deal_id,
        only_open=only_open,
        due_before=due_before,
        due_after=due_after
    )

@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(
    data: TaskCreate,
    current_user: User = Depends(get_current_user),
    organization_id: int = Depends(require_organization),
    role: str = Depends(check_organization_access),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new task for a deal.
    Due date must be in the future.
    Automatically creates activity log.
    """
    service = TaskService(db)
    return await service.create_task(
        organization_id=organization_id,
        user=current_user,
        role=role,
        data=data
    )

@router.patch("/{task_id}/mark-done", response_model=TaskResponse)
async def mark_task_done(
    task_id: int,
    current_user: User = Depends(get_current_user),
    organization_id: int = Depends(require_organization),
    role: str = Depends(check_organization_access),
    db: AsyncSession = Depends(get_db)
):
    """
    Mark a task as done.
    """
    service = TaskService(db)
    return await service.mark_task_done(
        task_id=task_id,
        organization_id=organization_id,
        user=current_user,
        role=role
    )
