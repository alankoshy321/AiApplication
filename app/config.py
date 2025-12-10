from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    weaviate_url: str = Field(default="http://localhost:8080", env="WEAVIATE_URL")
    weaviate_api_key: str | None = Field(default=None, env="WEAVIATE_API_KEY")
    collection_name: str = Field(default="Document", env="COLLECTION_NAME")
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2", env="EMBEDDING_MODEL"
    )
    gpt4all_model: str = Field(
        default="ggml-gpt4all-j-v1.3-groovy", env="GPT4ALL_MODEL"
    )
    data_path: str = Field(default="data/sample_docs", env="DATA_PATH")

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()



