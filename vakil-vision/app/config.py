from dotenv import load_dotenv
import os

load_dotenv()
load_dotenv("app/.env")

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/vakil_vision")

ALLOWED_EXTENSIONS = [".pdf", ".txt"]
MAX_FILE_SIZE_MB = 10
UPLOAD_DIR = "uploads"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
