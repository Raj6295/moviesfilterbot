# BolloFilterBot

A powerful Telegram bot for searching and filtering movie files with support for inline queries and various file types.

## Features

- 🔍 Fast and accurate search
- 📁 Support for various file types (videos, documents, audio, etc.)
- 🔎 Inline search support
- 📊 User statistics
- 👥 Admin panel
- 🔒 Secure file access

## Prerequisites

- Python 3.8 or higher
- MongoDB database
- Telegram Bot Token from [@BotFather](https://t.me/botfather)
- API ID and API Hash from [my.telegram.org](https://my.telegram.org/)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/billofilterbot.git
   cd billofilterbot
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root and add the following variables:
   ```env
   # Bot configuration
   BOT_TOKEN=your_bot_token_here
   BOT_USERNAME=your_bot_username
   
   # Telegram API credentials
   API_ID=your_api_id
   API_HASH=your_api_hash
   
   # MongoDB URI
   MONGO_DB_URI=mongodb+srv://username:password@cluster0.mongodb.net/database_name?retryWrites=true&w=majority
   
   # Channel/Chat IDs (optional)
   LOG_CHANNEL_ID=your_log_channel_id
   FILES_CHANNEL_ID=your_files_channel_id
   
   # Admin user IDs (comma-separated)
   ADMINS=123456789,987654321
   
   # Other settings
   AUTO_INDEX=False
   PORT=8082
   LOG_LEVEL=INFO
   ```

## Running the Bot

1. Start the bot:
   ```bash
   python bot.py
   ```

2. The bot should now be running and respond to commands.

## Available Commands

- `/start` - Start the bot and see welcome message
- `/help` - Show help message
- `/search [query]` - Search for files
- `/stats` - Show bot statistics (admin only)
- `/about` - Show information about the bot

## Inline Mode

You can use the bot in any chat by typing `@your_bot_username` followed by your search query.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For support, please open an issue or contact us at [@YourSupportChannel](https://t.me/YourSupportChannel)
