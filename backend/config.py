# Configuration file for API keys
import os

# Read Gemini API key from environment (set in Render dashboard)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
