from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    model_name: str = "cardiffnlp/twitter-xlm-roberta-base-sentiment"
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    max_text_length: int = 512
    
    # Настройки безопасности
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Настройки базы данных
    database_url: str = "sqlite:///./sentiment_analyzer.db"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()