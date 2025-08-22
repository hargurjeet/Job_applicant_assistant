import os

# Load from environment for security
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "########################")

# Model name
GEMINI_MODEL_NAME = "gemini-2.5-flash"
