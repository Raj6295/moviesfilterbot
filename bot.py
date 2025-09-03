#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import logging
import os
import sys
from aiohttp import web
from pyrogram import Client, idle
from pyrogram.errors import ApiIdInvalid, AccessTokenInvalid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Suppress some noisy logs
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("pyrogram.session").setLevel(logging.WARNING)
logging.getLogger("pyrogram.connection").setLevel(logging.WARNING)
logging.getLogger("aiohttp").setLevel(logging.WARNING)

# Initialize bot
bot = Client(
    "movie_filter_bot",
    api_id=os.environ.get("API_ID"),
    api_hash=os.environ.get("API_HASH"),
    bot_token=os.environ.get("BOT_TOKEN"),
    workers=200,
    plugins={
        "root": "handlers",
        "include": [
            "handlers.commands",
            "handlers.callbacks"
        ]
    }
)

# Import handlers explicitly to ensure they're loaded
import handlers

async def handle_health_check(request):
    """Handle health check requests"""
    return web.Response(text="Bot is running")

async def start_web_server():
    """Start a simple web server to keep the port open"""
    app = web.Application()
    app.router.add_get('/', handle_health_check)
    
    # Use the PORT environment variable if available, otherwise default to 8082
    port = int(os.environ.get('PORT', 8082))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logger.info(f"Web server started on port {port}")
    return runner, site

async def start_bot():
    """Start the bot with retry logic for flood waits"""
    retry_count = 0
    max_retries = 3
    
    while retry_count < max_retries:
        try:
            await bot.start()
            return await bot.get_me()
        except Exception as e:
            error_str = str(e)
            if "FLOOD_WAIT" in error_str:
                try:
                    # Extract wait time from error message
                    wait_time = int(error_str.split("A wait of ")[1].split(" ")[0])
                    retry_count += 1
                    logger.warning(f"⚠️ Flood wait for {wait_time} seconds. Retry {retry_count}/{max_retries}")
                    await asyncio.sleep(wait_time + 1)  # Add 1 second buffer
                except (IndexError, ValueError) as parse_error:
                    logger.error(f"❌ Error parsing flood wait time: {parse_error}")
                    raise Exception("Failed to parse flood wait time") from e
            else:
                raise
    
    raise Exception("Max retries exceeded for flood wait")

async def main():
    """Main function to start the bot and web server"""
    try:
        logger.info("🚀 Starting bot initialization...")
        
        # Start web server
        logger.info("🌐 Starting web server...")
        web_runner, web_site = await start_web_server()
        logger.info("✅ Web server started successfully")
        
        # Start the bot with retry logic
        logger.info("🤖 Starting bot client...")
        try:
            me = await start_bot()
            logger.info(f"✅ Bot started as @{me.username} (ID: {me.id})")
            
            # Initialize database
            from database.models import db
            await db.init_db()
            
            # Set bot commands
            logger.info("⌨️ Setting up bot commands...")
            from pyrogram.types import BotCommand
            
            commands = [
                BotCommand("start", "Start the bot"),
                BotCommand("help", "Show help message"),
                BotCommand("search", "Search for files"),
                BotCommand("stats", "Show bot statistics (Admin only)")
            ]
            await bot.set_bot_commands(commands)
            logger.info("✅ Bot commands set up successfully")
            
            # Keep the bot running
            logger.info("Bot and web server are now running.")
            await idle()
            
        except Exception as e:
            logger.error(f"❌ Error in bot initialization: {e}", exc_info=True)
            raise
            
    except ApiIdInvalid:
        logger.error("❌ Invalid API ID or API HASH. Please check your credentials.")
        sys.exit(1)
    except AccessTokenInvalid:
        logger.error("❌ Invalid bot token. Please check your bot token.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ An error occurred: {e}", exc_info=True)
        sys.exit(1)
    finally:
        # Stop the bot
        if 'bot' in locals() and await bot.is_connected:
            logger.info("🛑 Stopping bot...")
            await bot.stop()
            logger.info("✅ Bot stopped successfully")
            
        # Stop the web server
        if 'web_runner' in locals():
            logger.info("🌐 Stopping web server...")
            await web_runner.cleanup()
            logger.info("✅ Web server stopped")

if __name__ == "__main__":
    # Create a new event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("👋 Shutting down...")
    except Exception as e:
        logger.error(f"❌ An error occurred: {e}", exc_info=True)
    finally:
        # Cleanup
        if 'loop' in locals():
            loop.close()
        logger.info("✅ Bot has been stopped")
