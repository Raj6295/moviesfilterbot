import sys
import os
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from handlers.client import bot
from config import Config

@bot.on_message(filters.command("about") & (filters.private | filters.group))
async def about_command(client, message: Message):
    """Handle /about command"""
    about_text = (
        "🤖 **BolloFilterBot**\n\n"
        "A powerful Telegram bot for searching and filtering movie files.\n\n"
        "🔹 **Features:**\n"
        "• Fast and accurate search\n"
        "• Support for various file types\n"
        "• Inline search support\n"
        "• User-friendly interface\n\n"
        "🔧 **Technical Details:**\n"
        "• **Language:** Python 3.8+\n"
        "• **Framework:** Pyrogram\n"
        "• **Database:** MongoDB\n"
        "• **Version:** 1.0.0\n\n"
        "📝 **Source Code:**\n"
        "[GitHub Repository](https://github.com/yourusername/billofilterbot)\n\n"
        "📜 **License:**\n"
        "MIT License - Free to use and modify"
    )
    
    # Create keyboard
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📚 Help", callback_data="help_callback"),
            InlineKeyboardButton("🔍 Search Now", switch_inline_query_current_chat="")
        ],
        [
            InlineKeyboardButton("📢 Updates", url="https://t.me/BolloFilterUpdates"),
            InlineKeyboardButton("👥 Support", url="https://t.me/BolloFilterSupport")
        ]
    ])
    
    # Send about message
    await message.reply_text(
        about_text,
        reply_markup=keyboard,
        disable_web_page_preview=True
    )

# Callback query handler for about button
@bot.on_callback_query(filters.regex(r"^about_callback$"))
async def about_callback(client, callback_query):
    """Handle about button callback"""
    about_text = (
        "🤖 **BolloFilterBot**\n\n"
        "A powerful Telegram bot for searching and filtering movie files.\n\n"
        "🔹 **Features:**\n"
        "• Fast and accurate search\n"
        "• Support for various file types\n"
        "• Inline search support\n"
        "• User-friendly interface\n\n"
        "📝 **Source Code:**\n"
        "[GitHub Repository](https://github.com/yourusername/billofilterbot)"
    )
    
    # Create keyboard
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔙 Back", callback_data="back_to_help"),
            InlineKeyboardButton("🔍 Search Now", switch_inline_query_current_chat="")
        ]
    ])
    
    # Edit message with about text
    await callback_query.message.edit_text(
        about_text,
        reply_markup=keyboard,
        disable_web_page_preview=True
    )
    
    # Answer callback query
    await callback_query.answer()
