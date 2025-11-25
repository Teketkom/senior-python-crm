from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.schema import User
from src.repositories.base import BaseRepository

class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def create_user(self, email: str, hashed_password: str, name: str) -> User:
        user = User(
            email=email,
            hashed_password=hashed_password,
            name=name
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
