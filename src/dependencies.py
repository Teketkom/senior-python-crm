from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.security import decode_token
from src.repositories.user import UserRepository
from src.repositories.organization import OrganizationRepository
from src.models.schema import User

async def get_current_user(
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db)
) -> User:
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    token = authorization.replace("Bearer ", "")
    payload = decode_token(token)
    
    if payload is None or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user_id: int = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

async def get_organization_id(
    x_organization_id: Optional[int] = Header(None, alias="X-Organization-Id"),
) -> Optional[int]:
    return x_organization_id

async def require_organization(
    organization_id: Optional[int] = Depends(get_organization_id),
) -> int:
    if organization_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Organization-Id header is required"
        )
    return organization_id

async def check_organization_access(
    user: User = Depends(get_current_user),
    organization_id: int = Depends(require_organization),
    db: AsyncSession = Depends(get_db)
) -> str:
    org_repo = OrganizationRepository(db)
    role = await org_repo.get_user_role_in_org(user.id, organization_id)
    
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this organization"
        )
    
    return role

async def require_role(required_roles: list[str]):
    async def role_checker(
        role: str = Depends(check_organization_access)
    ) -> str:
        if role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {required_roles}"
            )
        return role
    return role_checker
