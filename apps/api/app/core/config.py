from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str = "mongodb://localhost:27017/slack_clone"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # JWT
    jwt_secret: str = "your-super-secret-jwt-key-32-bytes-long"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # MinIO
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "slack-clone"
    
    # LiveKit
    livekit_api_key: str = "devkey"
    livekit_api_secret: str = "secret"
    livekit_url: str = "ws://localhost:7880"
    
    # CORS
    cors_origins: list = ["http://localhost:3000", "http://localhost:8080"]
    
    class Config:
        env_file = ".env"

settings = Settings() 