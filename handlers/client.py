import logging
from typing import Dict, List, Optional, Union
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import BadRequest, UserNotParticipant, FloodWait

from ..config import Config
from ..database.models import Database

# Initialize logger
logger = logging.getLogger(__name__)

# Initialize database
db = Database(Config.MONGO_DB_URI)

class MovieBot(Client):
    """Main bot class that extends Pyrogram Client"""
    
    def __init__(self):
        """Initialize the bot with configuration"""
        super().__init__(
            Config.SESSION_NAME,
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            workers=200,
            plugins={"root": "handlers"}
        )
        
        # Initialize database
        self.db = db
        self.logger = logger
        
        # Store bot info
        self.bot_info = None
        self.bot_username = Config.BOT_USERNAME
        self.admins = Config.ADMINS
        
        # Store user data
        self.user_data = {}
        
        # Log initialization
        self.logger.info("✅ MovieBot initialized")
    
    async def start(self):
        """Start the bot client"""
        await super().start()
        
        # Initialize database
        await self.db.init_db()
        
        # Get bot info
        self.bot_info = await self.get_me()
        self.bot_username = self.bot_info.username
        
        # Log startup
        self.logger.info(f"✅ Bot started as @{self.bot_username} (ID: {self.bot_info.id})")
        self.logger.info(f"📊 Total admins: {len(self.admins)}")
    
    async def stop(self, *args):
        """Stop the bot client"""
        self.logger.info("🛑 Stopping bot...")
        await super().stop()
        self.logger.info("✅ Bot stopped successfully")
    
    async def is_admin(self, user_id: int) -> bool:
        """Check if a user is an admin"""
        return user_id in self.admins
    
    async def is_bot_admin(self, chat_id: int) -> bool:
        """Check if the bot is an admin in the chat"""
        try:
            member = await self.get_chat_member(chat_id, "me")
            return member.status in ["administrator", "creator"]
        except (BadRequest, UserNotParticipant):
            return False
    
    async def send_log_message(self, text: str, reply_markup: InlineKeyboardMarkup = None):
        """Send a log message to the log channel"""
        if not Config.LOG_CHANNEL_ID:
            return
            
        try:
            await self.send_message(
                chat_id=Config.LOG_CHANNEL_ID,
                text=text,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
        except Exception as e:
            self.logger.error(f"❌ Error sending log message: {e}")
    
    async def handle_error(self, update, context):
        """Handle errors in the bot"""
        self.logger.error(f"Error: {context.error}", exc_info=True)
        
        # Try to send error message to user
        try:
            if update.effective_message:
                await update.effective_message.reply_text(
                    "❌ An error occurred while processing your request. "
                    "The admin has been notified."
                )
        except Exception as e:
            self.logger.error(f"Error sending error message: {e}")
        
        # Send error to log channel
        error_msg = (
            f"⚠️ **Error in bot**\n\n"
            f"**Update:** {update}\n\n"
            f"**Error:** {context.error}\n\n"
            f"**Traceback:**\n```{context.error.__traceback__}```"
        )
        
        try:
            await self.send_log_message(error_msg)
        except Exception as e:
            self.logger.error(f"Error sending error to log channel: {e}")

# Initialize the bot
bot = MovieBot()

# Register error handler
@bot.on_errors()
async def error_handler(_, update, error):
    """Global error handler"""
    await bot.handle_error(update, error)
