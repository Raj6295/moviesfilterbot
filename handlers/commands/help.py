import sys
import os
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from handlers.client import bot
from config import Config

@bot.on_message(filters.command("help") & filters.private)
async def help_command(client, message: Message):
    """Handle /help command"""
    help_text = (
        "🤖 **BolloFilterBot Help**\n\n"
        "🔍 **How to search:**\n"
        "• Simply type the name of the movie you're looking for\n"
        "• Use specific keywords for better results\n"
        "• Example: `Avengers: Endgame 1080p`\n\n"
        "📋 **Available Commands:**\n"
        "• `/start` - Start the bot and see welcome message\n"
        "• `/search [query]` - Search for movies\n"
        "• `/stats` - Show bot statistics\n"
        "• `/about` - About this bot\n"
        "• `/help` - Show this help message\n\n"
        "🔗 **Inline Mode:**\n"
        "You can also use me in inline mode in any chat. Just type `@" + Config.BOT_USERNAME + " [query]`\n\n"
        "⚠️ **Note:**\n"
        "• Only files from authorized channels are indexed\n"
        "• Use proper keywords for better search results"
    )
    
    # Create keyboard
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔍 Search Now", switch_inline_query_current_chat=""),
            InlineKeyboardButton("📚 Commands", url=f"https://t.me/{Config.BOT_USERNAME}?start=help")
        ],
        [
            InlineKeyboardButton("📢 Updates", url="https://t.me/BolloFilterUpdates"),
            InlineKeyboardButton("👥 Support", url="https://t.me/BolloFilterSupport")
        ]
    ])
    
    # Send help message
    await message.reply_text(
        help_text,
        reply_markup=keyboard,
        disable_web_page_preview=True
    )
    
    # Log help command usage
    logger = client.logger
    logger.info(f"ℹ️ User {message.from_user.id} requested help")
