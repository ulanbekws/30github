from pydantic_settings import BaseSettings
import asyncpg

class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    @property
    def ASYNC_DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}: {self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".evn"

settings = Settings()

async def connect_db():
    return await asyncpg.connect(host="localhost",
                                 port=5432,
                                 user="postgres",
                                 password="123",
                                 database="postgres")