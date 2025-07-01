from typing import List, Dict, Any
from aiogram.types import BotCommand
from pydantic_settings import BaseSettings


class PostgresConfig(BaseSettings):
    NAME: str
    HOST: str
    PORT: int
    PASSWORD: str
    USER: str

    @property
    def URL(self) -> str:
        return f"postgresql+asyncpg://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.NAME}"

    class Config:
        env_prefix = 'POSTGRES_'
        env_file = '.env'
        extra = 'ignore'


class BotConfig(BaseSettings):
    TOKEN: str
    CHANEL_ID: int
    CHANEL_LINK: str
    ADMINS: list[int] | None = []
    SUPPORT_ID: int
    COMMANDS: list[BotCommand] = [
        BotCommand(command='start', description='Запустить бота 🚀')
    ]

    @property
    def SUPPORT_LINK(self) -> str:
        return f'tg://user?id={self.SUPPORT_ID}'

    class Config:
        env_prefix = 'BOT_'
        env_file = '.env'
        extra = 'ignore'


class Settings:
    
    def __init__(self):
        self.load()

    def load(self):
        self.postgres = PostgresConfig()
        self.bot = BotConfig()

    def reload(self):
        self.load()

settings = Settings()