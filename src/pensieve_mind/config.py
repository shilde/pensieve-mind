from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "pensieve"

    # Embedding model (runs locally)
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dimension: int = 384

    # Scraping
    scraper_timeout_seconds: int = 30
    scraper_max_content_length: int = 50_000

    class Config:
        env_file = ".env"

settings = Settings()
