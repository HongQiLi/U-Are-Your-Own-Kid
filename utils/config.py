#utils/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./dev.db"
    JWT_SECRET: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60*24
    CORS_ORIGINS: list[str] = ["http://localhost:3000","https://www.figma.com"]

settings = Settings()
