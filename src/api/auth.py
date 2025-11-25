from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from src.schemas.organization import OrganizationResponse
from src.services.auth_service import AuthService
from src.dependencies import get_current_user
from src.repositories.organization import OrganizationRepository
from src.models.schema import User

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user and create their organization.
    Returns JWT access and refresh tokens.
    """
    service = AuthService(db)
    return await service.register(request)

@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and return JWT tokens.
    """
    service = AuthService(db)
    return await service.login(request)

@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user information.
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        created_at=current_user.created_at.isoformat()
    )

@router.get("/organizations/me", response_model=list[OrganizationResponse])
async def get_my_organizations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all organizations the current user is a member of.
    """
    org_repo = OrganizationRepository(db)
    orgs = await org_repo.get_user_organizations(current_user.id)
    
    result = []
    for org in orgs:
        role = await org_repo.get_user_role_in_org(current_user.id, org.id)
        result.append(OrganizationResponse(
            id=org.id,
            name=org.name,
            created_at=org.created_at.isoformat(),
            role=role
        ))
    
    return result
