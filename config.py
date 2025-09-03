import os
import logging
from dotenv import load_dotenv
from typing import List, Optional

# Load environment variables from .env file
load_dotenv()

# Basic configuration
class Config:
    # Bot token from @BotFather
    BOT_TOKEN: str = os.environ.get("BOT_TOKEN", "")
    
    # Your API ID and hash from my.telegram.org
    API_ID: int = int(os.environ.get("API_ID", 0))
    API_HASH: str = os.environ.get("API_HASH", "")
    
    # MongoDB URI
    MONGO_DB_URI: str = os.environ.get("MONGO_DB_URI", "")
    
    # Channel IDs (as integers)
    LOG_CHANNEL_ID: int = int(os.environ.get("LOG_CHANNEL_ID", 0))
    FILES_CHANNEL_ID: int = int(os.environ.get("FILES_CHANNEL_ID", 0))
    
    # Bot username without @
    BOT_USERNAME: str = os.environ.get("BOT_USERNAME", "")
    
    # Admin user IDs (comma-separated)
    ADMINS: List[int] = [int(admin_id) for admin_id in os.environ.get("ADMINS", "").split(",") if admin_id]
    
    # Session name for Pyrogram
    SESSION_NAME: str = os.environ.get("SESSION_NAME", "movie_filter_bot")
    
    # Auto index files on startup
    AUTO_INDEX: bool = os.environ.get("AUTO_INDEX", "False").lower() == "true"
    
    # Web server configuration
    PORT: int = int(os.environ.get("PORT", 8082))
    
    # Log level
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO").upper()

# Validate required configurations
def validate_config() -> bool:
    """Validate the configuration and return True if all required fields are set"""
    required_vars = [
        ("BOT_TOKEN", Config.BOT_TOKEN),
        ("API_ID", Config.API_ID),
        ("API_HASH", Config.API_HASH),
        ("MONGO_DB_URI", Config.MONGO_DB_URI),
    ]
    
    missing_vars = [name for name, value in required_vars if not value]
    
    if missing_vars:
        logging.error(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    if not Config.ADMINS:
        logging.warning("⚠️  No admin users specified in ADMINS environment variable")
    
    return True

# Initialize logging
def setup_logging():
    """Set up logging configuration"""
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL, logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("bot.log")
        ]
    )
    
    # Suppress some noisy logs
    logging.getLogger("pyrogram").setLevel(logging.WARNING)
    logging.getLogger("pyrogram.session").setLevel(logging.WARNING)
    logging.getLogger("pyrogram.connection").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)

# Initialize logging when the module is imported
setup_logging()

# Log configuration status
if validate_config():
    logging.info("✅ Configuration loaded successfully")
else:
    logging.error("❌ Invalid configuration. Please check your environment variables.")
