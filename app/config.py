import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    FIRESTORE_PROJECT_ID: str = os.getenv("FIRESTORE_PROJECT_ID", "ai-job-tracker-kitchen")

settings = Settings()
