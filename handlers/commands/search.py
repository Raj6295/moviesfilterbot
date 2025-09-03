import logging
import sys
import os
from typing import List, Optional
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from handlers.client import bot
from config import Config
from database.models import db

logger = logging.getLogger(__name__)

@bot.on_message(filters.command("search") & (filters.private | filters.group))
async def search_command(client, message: Message):
    """Handle /search command"""
    # Check if query is provided
    if len(message.command) < 2:
        await message.reply_text(
            "🔍 **Please provide a search query**\n\n"
            "Example: `/search Avengers: Endgame 1080p`",
            quote=True
        )
        return
    
    # Extract search query
    query = " ".join(message.command[1:])
    user = message.from_user
    
    # Log search query
    logger.info(f"🔍 Search query from {user.id}: {query}")
    
    # Send searching message
    search_msg = await message.reply_text(
        f"🔍 Searching for **{query}**...",
        quote=True
    )
    
    try:
        # Search for files in database
        results = await db.search_files(query, limit=10)
        
        if not results:
            # No results found
            await search_msg.edit_text(
                f"❌ No results found for **{query}**\n\n"
                "Try with different keywords or check the spelling.",
                disable_web_page_preview=True
            )
            return
        
        # Prepare results message
        if len(results) == 1:
            result_text = f"🎬 **1 result found for** `{query}`"
        else:
            result_text = f"🎬 **{len(results)} results found for** `{query}`"
        
        # Create keyboard with results
        keyboard = []
        
        for i, result in enumerate(results[:10], 1):
            # Truncate long file names
            file_name = result['file_name']
            if len(file_name) > 50:
                file_name = file_name[:47] + '...'
                
            # Add button for each result
            keyboard.append([
                InlineKeyboardButton(
                    f"{i}. {file_name}",
                    callback_data=f"file_{result['file_id']}"
                )
            ])
        
        # Add navigation and help buttons
        keyboard.append([
            InlineKeyboardButton("🔍 New Search", switch_inline_query_current_chat=""),
            InlineKeyboardButton("ℹ️ Help", callback_data="help_callback")
        ])
        
        # Send results
        await search_msg.edit_text(
            result_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            disable_web_page_preview=True
        )
        
    except Exception as e:
        logger.error(f"Error in search command: {e}", exc_info=True)
        await search_msg.edit_text(
            "❌ An error occurred while searching. Please try again later."
        )

# Inline query handler
@bot.on_inline_query()
async def inline_search(client, inline_query):
    """Handle inline search queries"""
    query = inline_query.query.strip()
    
    if not query:
        # Show help if no query
        await inline_query.answer(
            results=[],
            switch_pm_text="🔍 Search for movies...",
            switch_pm_parameter="start"
        )
        return
    
    try:
        # Search for files in database
        results = await db.search_files(query, limit=50)
        
        if not results:
            # No results found
            await inline_query.answer(
                results=[],
                switch_pm_text="❌ No results found. Try again!",
                switch_pm_parameter="start"
            )
            return
        
        # Prepare inline results
        inline_results = []
        
        for result in results:
            # Create result item
            inline_results.append({
                "type": "article",
                "id": result['file_id'],
                "title": result['file_name'],
                "description": f"📁 {result['file_type'].upper()} • {result.get('file_size', 'N/A')}",
                "input_message_content": {
                    "message_text": f"🎬 **{result['file_name']}**\n\n"
                                    f"📁 Type: {result.get('file_type', 'Unknown')}\n"
                                    f"📦 Size: {result.get('file_size', 'N/A')}\n\n"
                                    f"🔍 Search: `{query}`",
                    "disable_web_page_preview": True
                },
                "reply_markup": InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(
                            "📥 Download",
                            callback_data=f"file_{result['file_id']}"
                        )
                    ]
                ])
            })
        
        # Send results
        await inline_query.answer(
            results=inline_results[:50],  # Max 50 results
            cache_time=1,
            is_personal=True
        )
        
    except Exception as e:
        logger.error(f"Error in inline search: {e}", exc_info=True)
        await inline_query.answer(
            results=[],
            switch_pm_text="❌ Error in search. Try again!",
            switch_pm_parameter="start"
        )
