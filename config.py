import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Model Configuration
DEFAULT_LLM_PROVIDER = "groq"  # "groq", "openai", or "anthropic"
OPENAI_MODEL = "gpt-4o"  # or "gpt-4-turbo-preview"
ANTHROPIC_MODEL = "claude-3-opus-20240229"
GROQ_MODEL = "groq/compound"

# OCR Configuration
# Auto-detected: /opt/homebrew/Cellar/tesseract/5.5.1/bin/tesseract
# Will auto-detect if None, or specify custom path
TESSERACT_CMD = None  # Auto-detect, or set to specific path like "/opt/homebrew/bin/tesseract"

# API Configuration
API_HOST = "0.0.0.0"
API_PORT = 8000


