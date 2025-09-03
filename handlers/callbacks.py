import logging
import sys
import os
from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from handlers.client import bot
from config import Config
from handlers.commands.help import help_command
from handlers.commands.about import about_callback

logger = logging.getLogger(__name__)

@bot.on_callback_query()
async def handle_callbacks(client, callback_query: CallbackQuery):
    """Handle all callback queries"""
    try:
        data = callback_query.data
        user = callback_query.from_user
        
        logger.info(f"Received callback: {data} from user {user.id}")
        
        # Route to appropriate handler based on callback data
        if data == "help_callback":
            await help_command(client, callback_query.message)
            await callback_query.answer()
            
        elif data == "about_callback":
            await about_callback(client, callback_query)
            
        elif data == "back_to_help":
            await help_command(client, callback_query.message)
            await callback_query.answer()
            
        elif data == "close_stats":
            # Let the stats command handle its own close callback
            return
            
        elif data == "refresh_stats":
            # Let the stats command handle its own refresh callback
            return
            
        elif data.startswith("file_"):
            await handle_file_callback(client, callback_query)
            
        else:
            logger.warning(f"Unknown callback data: {data}")
            await callback_query.answer("❌ Unknown action", show_alert=True)
            
    except Exception as e:
        logger.error(f"Error in callback handler: {e}", exc_info=True)
        try:
            await callback_query.answer("❌ An error occurred. Please try again.", show_alert=True)
        except:
            pass

async def handle_file_callback(client, callback_query: CallbackQuery):
    """Handle file download callbacks"""
    try:
        file_id = callback_query.data.split("_", 1)[1]
        user = callback_query.from_user
        
        logger.info(f"File download requested by {user.id}: {file_id}")
        
        # Get file info from database
        file_data = await client.db.files.find_one({"file_id": file_id})
        
        if not file_data:
            await callback_query.answer("❌ File not found in database.", show_alert=True)
            return
        
        # Send the file to the user
        try:
            # Send the file
            await client.send_cached_media(
                chat_id=user.id,
                file_id=file_id,
                caption=f"🎬 **{file_data.get('file_name', 'File')}**\n\n"
                        f"📁 Type: {file_data.get('file_type', 'Unknown')}\n"
                        f"📦 Size: {file_data.get('file_size', 'N/A')}\n\n"
                        f"🔗 [Share with friends](https://t.me/{Config.BOT_USERNAME}?start=file_{file_id})",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(
                            "🔍 Search Again",
                            switch_inline_query_current_chat=""
                        )
                    ]
                ])
            )
            
            # Notify user
            await callback_query.answer("📤 File sent to your private chat!", show_alert=True)
            
            # Log the download
            logger.info(f"File sent to user {user.id}: {file_id}")
            
            # Update download count in database
            await client.db.files.update_one(
                {"file_id": file_id},
                {"$inc": {"downloads": 1}},
                upsert=True
            )
            
        except Exception as e:
            logger.error(f"Error sending file {file_id} to user {user.id}: {e}")
            await callback_query.answer(
                "❌ Failed to send file. Please start a private chat with me and try again.",
                show_alert=True
            )
            
    except Exception as e:
        logger.error(f"Error in handle_file_callback: {e}", exc_info=True)
        await callback_query.answer("❌ An error occurred. Please try again.", show_alert=True)
