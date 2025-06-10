from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class DatabaseConfig(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    def get_db_url(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


database_config = DatabaseConfig()  # type: ignore


class RedisConfig(BaseSettings):
    REDIS_URL: str


cache_config = RedisConfig()  # type: ignore


class LogfireConfig(BaseSettings):
    LOGFIRE_TOKEN: str


logfire_config = LogfireConfig()  # type: ignore


class LLMConfig(BaseSettings):
    OPENAI_API_KEY: str


llm_config = LLMConfig()  # type: ignore
