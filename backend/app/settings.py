from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    PROVIDER: str = "sqlite"
    HOST: Optional[str]
    PORT: int = 8432
    USER: Optional[str]
    PASSWORD: Optional[str]
    DB_NAME: Optional[str]
    IN_MEMORY: Optional[int]


settings = Settings()
