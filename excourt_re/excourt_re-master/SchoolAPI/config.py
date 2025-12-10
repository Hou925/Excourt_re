# config.py
import os

from dotenv import load_dotenv

# load from .env
load_dotenv()


class Config:
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "123")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "school")
