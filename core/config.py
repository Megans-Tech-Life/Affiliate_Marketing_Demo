import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
   DATABASE_URL: str = os.getenv("DATABASE_URL")

   JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
   JWT_ALGORITHM: str = "HS256"
   JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

   PROJECT_NAME: str = "CRM Sales Pipeline API"
   PROJECT_VERSION: str = "1.0.0"

settings = Settings()