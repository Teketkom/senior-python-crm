from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.schema import Organization, OrganizationMember
from src.repositories.base import BaseRepository

class OrganizationRepository(BaseRepository[Organization]):
    def __init__(self, session: AsyncSession):
        super().__init__(Organization, session)

    async def get_by_name(self, name: str) -> Optional[Organization]:
        result = await self.session.execute(
            select(Organization).where(Organization.name == name)
        )
        return result.scalar_one_or_none()

    async def get_user_organizations(self, user_id: int):
        result = await self.session.execute(
            select(Organization)
            .join(OrganizationMember, Organization.id == OrganizationMember.organization_id)
            .where(OrganizationMember.user_id == user_id)
        )
        return list(result.scalars().all())

    async def get_user_role_in_org(self, user_id: int, org_id: int) -> Optional[str]:
        result = await self.session.execute(
            select(OrganizationMember.role)
            .where(
                OrganizationMember.user_id == user_id,
                OrganizationMember.organization_id == org_id
            )
        )
        return result.scalar_one_or_none()

    async def add_member(self, org_id: int, user_id: int, role: str) -> OrganizationMember:
        member = OrganizationMember(
            organization_id=org_id,
            user_id=user_id,
            role=role
        )
        self.session.add(member)
        await self.session.commit()
        await self.session.refresh(member)
        return member
