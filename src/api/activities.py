from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.schemas.activity import ActivityCreate, ActivityResponse
from src.services.activity_service import ActivityService
from src.dependencies import get_current_user, require_organization, check_organization_access
from src.models.schema import User

router = APIRouter(prefix="/api/v1", tags=["Activities"])

@router.get("/deals/{deal_id}/activities", response_model=list[ActivityResponse])
async def list_activities(
    deal_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    organization_id: int = Depends(require_organization),
    role: str = Depends(check_organization_access),
    db: AsyncSession = Depends(get_db)
):
    """
    Get activity log for a specific deal.
    Activities are ordered by created_at descending (newest first).
    """
    service = ActivityService(db)
    return await service.get_activities(
        deal_id=deal_id,
        organization_id=organization_id,
        user=current_user,
        role=role,
        page=page,
        page_size=page_size
    )

@router.post("/deals/{deal_id}/activities", response_model=ActivityResponse, status_code=201)
async def create_activity(
    deal_id: int,
    data: ActivityCreate,
    current_user: User = Depends(get_current_user),
    organization_id: int = Depends(require_organization),
    role: str = Depends(check_organization_access),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new activity (comment) on a deal.
    Only 'comment' type is allowed via this endpoint.
    System activities are auto-generated.
    """
    service = ActivityService(db)
    return await service.create_activity(
        deal_id=deal_id,
        organization_id=organization_id,
        user=current_user,
        role=role,
        data=data
    )
