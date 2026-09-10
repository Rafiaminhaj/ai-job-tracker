import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    FIRESTORE_PROJECT_ID: str = os.getenv("FIRESTORE_PROJECT_ID", "ai-job-tracker-kitchen")
    SENDER_EMAIL: str = os.getenv("SENDER_EMAIL", "rafiaminhaj423@gmail.com")
    SENDER_APP_PASSWORD: str = os.getenv("SENDER_APP_PASSWORD", "")

settings = Settings()
