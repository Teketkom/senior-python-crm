from typing import List, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.schema import Deal, DealStatus, DealStage

class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_deals_summary(
        self,
        organization_id: int,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Returns summary: total deals count, total amount, won amount, avg deal size.
        Last N days.
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Total deals and amount
        result = await self.db.execute(
            select(
                func.count(Deal.id).label("total_count"),
                func.sum(Deal.amount).label("total_amount")
            )
            .where(
                and_(
                    Deal.organization_id == organization_id,
                    Deal.created_at >= cutoff_date
                )
            )
        )
        row = result.first()
        total_count = row.total_count or 0
        total_amount = row.total_amount or Decimal(0)
        
        # Won deals and amount
        result_won = await self.db.execute(
            select(
                func.count(Deal.id).label("won_count"),
                func.sum(Deal.amount).label("won_amount")
            )
            .where(
                and_(
                    Deal.organization_id == organization_id,
                    Deal.status == DealStatus.won,
                    Deal.created_at >= cutoff_date
                )
            )
        )
        row_won = result_won.first()
        won_count = row_won.won_count or 0
        won_amount = row_won.won_amount or Decimal(0)
        
        avg_deal_size = total_amount / total_count if total_count > 0 else Decimal(0)
        
        return {
            "period_days": days,
            "total_deals_count": total_count,
            "total_amount": float(total_amount),
            "won_deals_count": won_count,
            "won_amount": float(won_amount),
            "average_deal_size": float(avg_deal_size)
        }

    async def get_deals_funnel(
        self,
        organization_id: int
    ) -> List[Dict[str, Any]]:
        """
        Returns count of deals per stage.
        """
        result = await self.db.execute(
            select(
                Deal.stage,
                func.count(Deal.id).label("count")
            )
            .where(Deal.organization_id == organization_id)
            .group_by(Deal.stage)
        )
        
        funnel = []
        for row in result:
            funnel.append({
                "stage": row.stage.value,
                "count": row.count
            })
        
        return funnel
