import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "ViraNova API"
    PROJECT_VERSION: str = "1.0.0"
    
    # API Keys
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")
    RUNWAY_API_KEY: str = os.getenv("RUNWAY_API_KEY", "")
    
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_ENVIRONMENT: str = os.getenv("PINECONE_ENVIRONMENT", "us-east-1-aws")
    
    # Scrapers
    REDDIT_CLIENT_ID: str = os.getenv("REDDIT_CLIENT_ID", "")
    REDDIT_CLIENT_SECRET: str = os.getenv("REDDIT_CLIENT_SECRET", "")
    YOUTUBE_API_KEY: str = os.getenv("YOUTUBE_API_KEY", "")
    NEWS_API_KEY: str = os.getenv("NEWS_API_KEY", "")
    
    # App Env
    APP_ENV: str = os.getenv("APP_ENV", "development")
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")

settings = Settings()
