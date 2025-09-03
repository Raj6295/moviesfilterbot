from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from ..client import bot
from ...config import Config
from ...database.models import db

@bot.on_message(filters.command("start") & filters.private)
async def start_command(client, message: Message):
    """Handle /start command"""
    user = message.from_user
    
    # Add user to database
    await db.add_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name
    )
    
    # Create welcome message
    welcome_text = (
        f"👋 **Hello {user.mention}!**\n\n"
        "🤖 **Welcome to BolloFilterBot!**\n"
        "I can help you find and filter movie files from our database.\n\n"
        "🔍 **How to use me:**\n"
        "• Just send me the name of the movie you're looking for\n"
        "• I'll search through our database and show you matching results\n"
        "• Click on the result to get the file\n\n"
        "📌 **Available Commands:**\n"
        "/search` [query]` - Search for movies\n"
        "`/help` - Show this help message\n"
        "`/stats` - Show bot statistics\n"
        "/about` - About this bot"
    )
    
    # Create keyboard
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔍 Search Movies", switch_inline_query_current_chat=""),
            InlineKeyboardButton("📚 Help", callback_data="help_callback")
        ],
        [
            InlineKeyboardButton("📊 Stats", callback_data="stats_callback"),
            InlineKeyboardButton("ℹ️ About", callback_data="about_callback")
        ]
    ])
    
    # Send welcome message
    await message.reply_text(
        welcome_text,
        reply_markup=keyboard,
        disable_web_page_preview=True
    )
    
    # Log user start
    logger = client.logger
    logger.info(f"👤 User {user.id} started the bot")
    
    # Send log to admin
    if Config.LOG_CHANNEL_ID:
        log_text = (
            f"👤 **New User**\n"
            f"├ User: {user.mention} (`{user.id}`)\n"
            f"├ Username: @{user.username}\n"
            f"└ First Name: `{user.first_name}`"
        )
        await client.send_message(
            chat_id=Config.LOG_CHANNEL_ID,
            text=log_text,
            disable_web_page_preview=True
        )
