from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from src.repositories.user import UserRepository
from src.repositories.organization import OrganizationRepository
from src.security import hash_password, verify_password, create_access_token, create_refresh_token
from src.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from src.models.schema import User

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.org_repo = OrganizationRepository(db)

    async def register(self, request: RegisterRequest) -> TokenResponse:
        # Check if user exists
        existing_user = await self.user_repo.get_by_email(request.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists"
            )
        
        # Create user
        hashed_pwd = hash_password(request.password)
        user = await self.user_repo.create_user(
            email=request.email,
            hashed_password=hashed_pwd,
            name=request.name
        )
        
        # Create organization
        org = await self.org_repo.create(name=request.organization_name)
        
        # Add user as owner
        await self.org_repo.add_member(
            org_id=org.id,
            user_id=user.id,
            role="owner"
        )
        
        # Generate tokens
        access_token = create_access_token(data={"sub": user.id})
        refresh_token = create_refresh_token(data={"sub": user.id})
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )

    async def login(self, request: LoginRequest) -> TokenResponse:
        user = await self.user_repo.get_by_email(request.email)
        
        if not user or not verify_password(request.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        access_token = create_access_token(data={"sub": user.id})
        refresh_token = create_refresh_token(data={"sub": user.id})
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )
