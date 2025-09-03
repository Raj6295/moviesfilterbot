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
    plugins={"root": "handlers"}
)

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

async def main():
    """Main function to start the bot and web server"""
    try:
        logger.info("🚀 Starting bot initialization...")
        
        # Start web server
        logger.info("🌐 Starting web server...")
        web_runner, web_site = await start_web_server()
        logger.info("✅ Web server started successfully")
        
        # Start the bot
        logger.info("🤖 Starting bot client...")
        await bot.start()
        
        # Verify bot is running
        try:
            me = await bot.get_me()
            logger.info(f"✅ Bot started as @{me.username} (ID: {me.id})")
        except Exception as e:
            logger.error(f"❌ Failed to get bot info: {e}")
            raise
        
        # Set bot commands
        logger.info("⌨️ Setting up bot commands...")
        await bot.set_bot_commands([
            ("start", "Start the bot"),
            ("help", "Show help message"),
            ("stats", "Show bot statistics"),
            ("index", "Index all files from the channel (Admin only)")
        ])
        logger.info("✅ Bot commands set up successfully")
        
        # Keep the bot running
        logger.info("Bot and web server are now running.")
        await idle()
            
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
