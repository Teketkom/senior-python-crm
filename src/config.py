from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://crm_user:strongpassword@localhost:5432/crm"
    jwt_secret: str = "ChangeMeToSecretKey"
    jwt_algorithm: str = "HS256"
    access_token_expires_minutes: int = 30
    refresh_token_expires_minutes: int = 60*24*7
    class Config:
        env_file = ".env"

def get_settings() -> Settings:
    return Settings()
