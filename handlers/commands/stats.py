import time
from datetime import datetime, timedelta
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from ..client import bot
from ...config import Config
from ...database.models import db

@bot.on_message(filters.command("stats") & (filters.private | filters.group))
async def stats_command(client, message: Message):
    """Handle /stats command"""
    # Check if user is admin
    user = message.from_user
    if user.id not in Config.ADMINS:
        await message.reply_text("❌ You don't have permission to view stats.")
        return
    
    # Send processing message
    stats_msg = await message.reply_text("📊 Fetching statistics...", quote=True)
    
    try:
        # Get stats from database
        stats = await db.get_stats()
        
        # Calculate uptime
        start_time = client.start_time
        uptime = datetime.utcnow() - start_time
        days, remainder = divmod(int(uptime.total_seconds()), 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, _ = divmod(remainder, 60)
        
        # Format stats message
        stats_text = (
            "🤖 **Bot Statistics**\n\n"
            f"👥 **Total Users:** `{stats['total_users']:,}`\n"
            f"📂 **Total Files:** `{stats['total_files']:,}`\n"
            f"💬 **Total Chats:** `{stats['total_chats']:,}`\n\n"
            f"⏱ **Uptime:** {days}d {hours}h {minutes}m\n"
            f"🚀 **Start Time:** `{start_time.strftime('%Y-%m-%d %H:%M:%S')} UTC`\n\n"
            "_Last updated: {}".format(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"))
        )
        
        # Create keyboard
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔄 Refresh", callback_data="refresh_stats"),
                InlineKeyboardButton("❌ Close", callback_data="close_stats")
            ]
        ])
        
        # Send stats message
        await stats_msg.edit_text(
            stats_text,
            reply_markup=keyboard,
            disable_web_page_preview=True
        )
        
    except Exception as e:
        logger = client.logger
        logger.error(f"Error in stats command: {e}", exc_info=True)
        await stats_msg.edit_text(
            "❌ An error occurred while fetching statistics. Please try again later."
        )

@bot.on_callback_query(filters.regex(r"^refresh_stats$"))
async def refresh_stats_callback(client, callback_query):
    """Handle refresh stats button"""
    # Check if user is admin
    user = callback_query.from_user
    if user.id not in Config.ADMINS:
        await callback_query.answer("❌ You don't have permission to refresh stats.", show_alert=True)
        return
    
    # Answer callback with loading message
    await callback_query.answer("🔄 Refreshing statistics...")
    
    try:
        # Get updated stats
        stats = await db.get_stats()
        
        # Calculate uptime
        start_time = client.start_time
        uptime = datetime.utcnow() - start_time
        days, remainder = divmod(int(uptime.total_seconds()), 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, _ = divmod(remainder, 60)
        
        # Format stats message
        stats_text = (
            "🤖 **Bot Statistics**\n\n"
            f"👥 **Total Users:** `{stats['total_users']:,}`\n"
            f"📂 **Total Files:** `{stats['total_files']:,}`\n"
            f"💬 **Total Chats:** `{stats['total_chats']:,}`\n\n"
            f"⏱ **Uptime:** {days}d {hours}h {minutes}m\n"
            f"🚀 **Start Time:** `{start_time.strftime('%Y-%m-%d %H:%M:%S')} UTC`\n\n"
            "_Last updated: {}".format(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"))
        )
        
        # Update message
        await callback_query.message.edit_text(
            stats_text,
            reply_markup=callback_query.message.reply_markup,
            disable_web_page_preview=True
        )
        
    except Exception as e:
        logger = client.logger
        logger.error(f"Error refreshing stats: {e}", exc_info=True)
        await callback_query.answer("❌ Failed to refresh statistics.", show_alert=True)

@bot.on_callback_query(filters.regex(r"^close_stats$"))
async def close_stats_callback(client, callback_query):
    """Handle close stats button"""
    # Check if user is the one who initiated the command
    if callback_query.from_user.id != callback_query.message.reply_to_message.from_user.id:
        await callback_query.answer("❌ You didn't request these stats.", show_alert=True)
        return
    
    # Delete the message
    await callback_query.message.delete()
    await callback_query.answer("❌ Statistics closed.")
