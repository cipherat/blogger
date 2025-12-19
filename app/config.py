from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    BLOGGER_DB_NAME: str = "blogger_db"
    BLOGGER_DB_USER: str = "blogger_user"
    BLOGGER_DB_PASS: str = "your_password"
    BLOGGER_DB_HOST: str = "database"
    BLOGGER_DB_PORT: str = "5432"

    BLOGGER_IS_ADMIN: bool = False
    #BLOGGER_CONTENT_DIR: str = "/app/data/blogs"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
