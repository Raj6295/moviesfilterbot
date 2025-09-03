import logging
import sys
import os
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Dict, List, Optional, Union
from bson import ObjectId

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config

class Database:
    """Database class to handle all database operations"""
    
    def __init__(self, uri: str, database_name: str = "movie_filter_bot"):
        """Initialize the database connection"""
        try:
            self._client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=5000)
            self.db = self._client.get_database(database_name)
            self.users = self.db.users
            self.files = self.db.files
            self.chats = self.db.chats
            self.logger = logging.getLogger(__name__)
            # Test the connection
            self._client.admin.command('ping')
        except Exception as e:
            self.logger.error(f"❌ Failed to connect to MongoDB: {e}")
            raise
        
    async def init_db(self):
        """Initialize database indexes with proper error handling"""
        try:
            # Drop existing indexes to avoid conflicts
            try:
                await self.users.drop_index("user_id_1")
            except Exception as e:
                if "index not found" not in str(e).lower():
                    self.logger.warning(f"⚠️ Error dropping user_id index: {e}")
            
            # Create indexes with explicit names and options
            await self.users.create_index(
                [("user_id", 1)],
                name="user_id_unique",
                unique=True
            )
            
            # Create text index for file search
            try:
                await self.files.create_index(
                    [("file_name", "text")],
                    name="file_name_text"
                )
            except Exception as e:
                if "text index already exists" not in str(e).lower():
                    raise
                
            # Create unique index for file_id
            await self.files.create_index(
                [("file_id", 1)],
                name="file_id_unique",
                unique=True
            )
            
            # Create unique index for chat_id
            await self.chats.create_index(
                [("chat_id", 1)],
                name="chat_id_unique",
                unique=True
            )
            
            self.logger.info("✅ Database indexes verified/created successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing database indexes: {e}", exc_info=True)
            return False
    
    # User-related methods
    async def add_user(self, user_id: int, username: str = "", first_name: str = ""):
        """Add a new user to the database"""
        try:
            user = {
                "user_id": user_id,
                "username": username,
                "first_name": first_name,
                "banned": False,
                "join_date": datetime.utcnow()
            }
            await self.users.update_one({"user_id": user_id}, {"$set": user}, upsert=True)
            self.logger.info(f"✅ User {user_id} added/updated in database")
            return True
        except Exception as e:
            self.logger.error(f"❌ Error adding user to database: {e}")
            return False
    
    async def get_user(self, user_id: int) -> Optional[Dict]:
        """Get a user from the database"""
        try:
            user = await self.users.find_one({"user_id": user_id})
            return user
        except Exception as e:
            self.logger.error(f"❌ Error getting user from database: {e}")
            return None
    
    async def is_user_banned(self, user_id: int) -> bool:
        """Check if a user is banned"""
        try:
            user = await self.get_user(user_id)
            if user:
                return user.get("banned", False)
            return False
        except Exception as e:
            self.logger.error(f"❌ Error checking if user is banned: {e}")
            return False
    
    # File-related methods
    async def add_file(self, file_id: str, file_name: str, file_type: str, file_size: int, 
                      mime_type: str = "", caption: str = "", chat_id: int = None) -> bool:
        """Add a new file to the database"""
        try:
            file = {
                "file_id": file_id,
                "file_name": file_name,
                "file_type": file_type,
                "file_size": file_size,
                "mime_type": mime_type,
                "caption": caption,
                "chat_id": chat_id,
                "date_added": datetime.utcnow()
            }
            await self.files.update_one({"file_id": file_id}, {"$set": file}, upsert=True)
            self.logger.info(f"✅ File {file_id} added/updated in database")
            return True
        except Exception as e:
            self.logger.error(f"❌ Error adding file to database: {e}")
            return False
    
    async def search_files(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for files in the database"""
        try:
            # Using text search if available, otherwise use regex
            if await self.files.index_information().get("file_name_text"):
                cursor = self.files.find(
                    {"$text": {"$search": query}},
                    {"score": {"$meta": "textScore"}}
                ).sort([("score", {"$meta": "textScore"})])
            else:
                cursor = self.files.find({"file_name": {"$regex": query, "$options": "i"}})
            
            return await cursor.to_list(length=limit)
        except Exception as e:
            self.logger.error(f"❌ Error searching files: {e}")
            return []
    
    # Chat-related methods
    async def add_chat(self, chat_id: int, chat_type: str, title: str = "") -> bool:
        """Add a chat to the database"""
        try:
            chat = {
                "chat_id": chat_id,
                "type": chat_type,
                "title": title,
                "date_added": datetime.utcnow()
            }
            await self.chats.update_one({"chat_id": chat_id}, {"$set": chat}, upsert=True)
            self.logger.info(f"✅ Chat {chat_id} added/updated in database")
            return True
        except Exception as e:
            self.logger.error(f"❌ Error adding chat to database: {e}")
            return False
    
    # Stats methods
    async def get_stats(self) -> Dict[str, int]:
        """Get bot statistics"""
        try:
            total_users = await self.users.count_documents({})
            total_files = await self.files.count_documents({})
            total_chats = await self.chats.count_documents({})
            
            return {
                "total_users": total_users,
                "total_files": total_files,
                "total_chats": total_chats
            }
        except Exception as e:
            self.logger.error(f"❌ Error getting stats: {e}")
            return {
                "total_users": 0,
                "total_files": 0,
                "total_chats": 0
            }

# Initialize database
db = Database(Config.MONGO_DB_URI)
