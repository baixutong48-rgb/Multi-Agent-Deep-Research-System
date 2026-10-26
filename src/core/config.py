from pydantic import BaseModel
from pydantic_settings import SettingsConfigDict,BaseSettings
from functools import lru_cache

class LLMSettings(BaseModel):
    provider: str
    model_name: str
    api_key: str | None = None
    base_url: str | None = None
    temperature: float = 0.0
    timeout: float = 30.0

# class DatabaseSettings(BaseModel):
#     url: str
#     query_timeout: float = 10.0
#     max_rows: int = 100

# class KnowledgeSettings(BaseModel):
#     base_url: str
#     api_key: str | None = None
#     timeout: float = 20.0
#     top_k: int = 5

class WorkspaceSettings(BaseModel):
    root: str = "data/runs"
    max_read_bytes: int = 5 * 1024 * 1024

class TavilySearchSettings(BaseModel):
    api_key : str
    timeout: float

class Settings(BaseSettings):
    llm : LLMSettings
    # db:DatabaseSettings
    # knowledge: KnowledgeSettings
    workspace: WorkspaceSettings
    tavily:TavilySearchSettings
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
        env_nested_delimiter='__'
    )


@lru_cache
def get_setting()->Settings:
    return Settings()

    
