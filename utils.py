import logging
import re
from typing import Optional, Tuple, Dict, Any
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

logger = logging.getLogger(__name__)

def parse_file_size(size_bytes: int) -> str:
    """Convert file size in bytes to human readable format"""
    if not size_bytes:
        return "0 B"
    
    size_names = ("B", "KB", "MB", "GB", "TB")
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    
    return f"{size_bytes:.2f} {size_names[i]}"

def escape_markdown(text: str) -> str:
    """Escape special Markdown characters"""
    if not text:
        return ""
    
    escape_chars = r'\*_`[\]()~>#+-=|{}.!'
    return ''.join(f'\\{char}' if char in escape_chars else char for char in text)

def parse_caption(caption: str, max_length: int = 100) -> str:
    """Parse and sanitize caption text"""
    if not caption:
        return ""
    
    # Remove multiple spaces and newlines
    caption = ' '.join(caption.split())
    
    # Truncate if too long
    if len(caption) > max_length:
        caption = caption[:max_length - 3] + '...'
    
    return escape_markdown(caption)

def get_media_info(message: Message) -> Optional[Dict[str, Any]]:
    """Extract media information from a message"""
    if not message or not message.media:
        return None
    
    media_info = {
        "file_id": None,
        "file_name": "",
        "file_size": 0,
        "mime_type": "",
        "file_type": "unknown"
    }
    
    # Handle different media types
    if message.audio:
        media = message.audio
        media_info["file_type"] = "audio"
    elif message.document:
        media = message.document
        media_info["file_type"] = media.mime_type.split('/')[-1] if media.mime_type else "document"
    elif message.video:
        media = message.video
        media_info["file_type"] = "video"
    elif message.voice:
        media = message.voice
        media_info["file_type"] = "voice"
    elif message.video_note:
        media = message.video_note
        media_info["file_type"] = "video_note"
    elif message.photo:
        # Get the largest photo size
        media = sorted(message.photo, key=lambda p: p.file_size, reverse=True)[0]
        media_info["file_type"] = "photo"
    else:
        return None
    
    # Extract file info
    media_info["file_id"] = media.file_id
    media_info["file_size"] = media.file_size
    media_info["mime_type"] = getattr(media, "mime_type", "")
    
    # Get file name if available
    if hasattr(media, "file_name") and media.file_name:
        media_info["file_name"] = media.file_name
    elif message.caption:
        # Try to extract filename from caption
        caption = message.caption
        # Look for common file name patterns in caption
        match = re.search(r'([^/\\&?]+\.[a-zA-Z0-9]+)(?:\?.*)?$', caption)
        if match:
            media_info["file_name"] = match.group(1).strip()
    
    # If still no filename, create a generic one
    if not media_info["file_name"]:
        ext = media_info["mime_type"].split('/')[-1] if media_info["mime_type"] else media_info["file_type"]
        media_info["file_name"] = f"file_{media.file_id[:8]}.{ext}"
    
    return media_info

def create_pagination_buttons(page: int, total_pages: int, prefix: str) -> InlineKeyboardMarkup:
    """Create pagination buttons for search results"""
    keyboard = []
    
    # Previous button
    prev_btn = InlineKeyboardButton("⬅️ Prev", callback_data=f"{prefix}_page_{page-1}" if page > 1 else "noop")
    
    # Page info
    page_btn = InlineKeyboardButton(f"📄 {page}/{total_pages}", callback_data="noop")
    
    # Next button
    next_btn = InlineKeyboardButton("Next ➡️", callback_data=f"{prefix}_page_{page+1}" if page < total_pages else "noop")
    
    # Add buttons to keyboard
    keyboard.append([prev_btn, page_btn, next_btn])
    
    # Add close button
    keyboard.append([InlineKeyboardButton("❌ Close", callback_data="close_pagination")])
    
    return InlineKeyboardMarkup(keyboard)
