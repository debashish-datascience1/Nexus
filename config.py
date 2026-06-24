import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY   = os.getenv("GOOGLE_API_KEY", "")
GITHUB_TOKEN     = os.getenv("GITHUB_TOKEN", "")
NEWSAPI_KEY      = os.getenv("NEWSAPI_KEY", "")
LINKEDIN_EMAIL   = os.getenv("LINKEDIN_EMAIL", "")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD", "")

MODEL_NAME = "gemini-1.5-flash"
DB_PATH    = Path(__file__).parent / "memory" / "agent_memory.db"
