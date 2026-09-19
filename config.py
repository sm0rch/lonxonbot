"""
config.py — Central configuration loader.
Reads all secrets from .env and exposes them as constants.
"""
import os
from dotenv import load_dotenv

# Load variables from .env file into environment
load_dotenv()

# Telegram
TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_TOKEN", "")

# DNSE API
DNSE_USERNAME: str = os.getenv("DNSE_USERNAME", "")
DNSE_PASSWORD: str = os.getenv("DNSE_PASSWORD", "")


def validate():
    """Check that all required environment variables are set."""
    missing = []
    if not TELEGRAM_TOKEN:
        missing.append("TELEGRAM_TOKEN")
    if not DNSE_USERNAME:
        missing.append("DNSE_USERNAME")
    if not DNSE_PASSWORD:
        missing.append("DNSE_PASSWORD")

    if missing:
        raise EnvironmentError(
            f"❌ Missing required environment variables: {', '.join(missing)}\n"
            "Please fill them in your .env file."
        )
    print("✅ All environment variables loaded successfully.")
