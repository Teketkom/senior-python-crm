from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.services.analytics_service import AnalyticsService
from src.dependencies import get_current_user, require_organization, check_organization_access, require_role
from src.models.schema import User

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])

@router.get("/deals/summary")
async def get_deals_summary(
    days: int = Query(30, ge=1),
    current_user: User = Depends(get_current_user),
    organization_id: int = Depends(require_organization),
    role: str = Depends(check_organization_access),
    db: AsyncSession = Depends(get_db)
):
    """
    Get deals summary statistics for the last N days.
    Returns: total deals count, total amount, won deals count, won amount, average deal size.
    """
    service = AnalyticsService(db)
    return await service.get_deals_summary(
        organization_id=organization_id,
        days=days
    )

@router.get("/deals/funnel")
async def get_deals_funnel(
    current_user: User = Depends(get_current_user),
    organization_id: int = Depends(require_organization),
    role: str = Depends(check_organization_access),
    db: AsyncSession = Depends(get_db)
):
    """
    Get deals funnel - count of deals per stage.
    """
    service = AnalyticsService(db)
    return await service.get_deals_funnel(
        organization_id=organization_id
    )
