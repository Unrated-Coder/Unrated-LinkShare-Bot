
import motor.motor_asyncio
import base64
from config import DB_URI, DB_NAME
from datetime import datetime, timedelta
from typing import List, Optional

dbclient = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
database = dbclient[DB_NAME]

# collections
user_data = database['users']
channels_collection = database['channels']
fsub_channels_collection = database['fsub_channels']

async def add_user(user_id: int) -> bool:
    """Add a user to the database if they don't exist."""
    if not isinstance(user_id, int) or user_id <= 0:
        print(f"Invalid user_id: {user_id}")
        return False
    
    try:
        existing_user = await user_data.find_one({'_id': user_id})
        if existing_user:
            return False
        
        await user_data.insert_one({'_id': user_id, 'created_at': datetime.utcnow()})
        return True
    except Exception as e:
        print(f"Error adding user {user_id}: {e}")
        return False

async def present_user(user_id: int) -> bool:
    """Check if a user exists in the database."""
    if not isinstance(user_id, int):
        return False
    return bool(await user_data.find_one({'_id': user_id}))

async def full_userbase() -> List[int]:
    """Get all user IDs from the database."""
    try:
        user_docs = user_data.find()
        return [doc['_id'] async for doc in user_docs]
    except Exception as e:
        print(f"Error fetching userbase: {e}")
        return []

async def count_users() -> int:
    """Count total users in the database."""
    try:
        return await user_data.count_documents({})
    except Exception as e:
        print(f"Error counting users: {e}")
        return 0

async def del_user(user_id: int) -> bool:
    """Delete a user from the database."""
    try:
        result = await user_data.delete_one({'_id': user_id})
        return result.deleted_count > 0
    except Exception as e:
        print(f"Error deleting user {user_id}: {e}")
        return False

async def is_admin(user_id: int) -> bool:
    """Check if a user is an admin."""
    admins_collection = database['admins']
    try:
        user_id = int(user_id)  # Ensure always int
        return bool(await admins_collection.find_one({'_id': user_id}))
    except Exception as e:
        print(f"Error checking admin status for {user_id}: {e}")
        return False

async def add_admin(user_id: int) -> bool:
    """Add a user as admin."""
    admins_collection = database['admins']
    try:
        user_id = int(user_id)  # Ensure always int
        await admins_collection.update_one({'_id': user_id}, {'$set': {'_id': user_id}}, upsert=True)
        return True
    except Exception as e:
        print(f"Error adding admin {user_id}: {e}")
        return False

async def remove_admin(user_id: int) -> bool:
    """Remove a user from admins."""
    admins_collection = database['admins']
    try:
        result = await admins_collection.delete_one({'_id': user_id})
        return result.deleted_count > 0
    except Exception as e:
        print(f"Error removing admin {user_id}: {e}")
        return False

async def list_admins() -> list:
    """List all admin user IDs."""
    admins_collection = database['admins']
    try:
        admins = await admins_collection.find().to_list(None)
        return [admin['_id'] for admin in admins]
    except Exception as e:
        print(f"Error listing admins: {e}")
        return []

async def save_channel(channel_id: int) -> bool:
    """Save a channel to the database with invite link expiration."""
    if not isinstance(channel_id, int):
        print(f"Invalid channel_id: {channel_id}")
        return False
    
    try:
        await channels_collection.update_one(
            {"channel_id": channel_id},
            {
                "$set": {
                    "channel_id": channel_id,
                    "invite_link_expiry": None,
                    "created_at": datetime.utcnow(),
                    "status": "active"
                }
            },
            upsert=True
        )
        return True
    except Exception as e:
        print(f"Error saving channel {channel_id}: {e}")
        return False

async def get_channels() -> List[int]:
    """Get all active channel IDs from the database."""
    try:
        channels = await channels_collection.find({"status": "active"}).to_list(None)
        valid_channels = []
        for channel in channels:
            if isinstance(channel, dict) and "channel_id" in channel:
                valid_channels.append(channel["channel_id"])
            else:
                print(f"Invalid channel document: {channel}")
        if not valid_channels:
            print(f"No valid channels found in database. Total documents checked: {len(channels)}")
        return valid_channels
    except Exception as e:
        print(f"Error fetching channels: {e}")
        return []

async def delete_channel(channel_id: int) -> bool:
    """Delete a channel from the database."""
    try:
        result = await channels_collection.delete_one({"channel_id": channel_id})
        return result.deleted_count > 0
    except Exception as e:
        print(f"Error deleting channel {channel_id}: {e}")
        return False

async def save_encoded_link(channel_id: int) -> Optional[str]:
    """Save an encoded link for a channel and return it."""
    if not isinstance(channel_id, int):
        print(f"Invalid channel_id: {channel_id}")
        return None
    
    try:
        encoded_link = base64.urlsafe_b64encode(str(channel_id).encode()).decode()
        await channels_collection.update_one(
            {"channel_id": channel_id},
            {
                "$set": {
                    "encoded_link": encoded_link,
                    "status": "active",
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        return encoded_link
    except Exception as e:
        print(f"Error saving encoded link for channel {channel_id}: {e}")
        return None

async def get_channel_by_encoded_link(encoded_link: str) -> Optional[int]:
    """Get a channel ID by its encoded link."""
    if not isinstance(encoded_link, str):
        return None
    
    try:
        channel = await channels_collection.find_one({"encoded_link": encoded_link, "status": "active"})
        return channel["channel_id"] if channel and "channel_id" in channel else None
    except Exception as e:
        print(f"Error fetching channel by encoded link {encoded_link}: {e}")
        return None

async def save_encoded_link2(channel_id: int, encoded_link: str) -> Optional[str]:
    """Save a secondary encoded link for a channel."""
    if not isinstance(channel_id, int) or not isinstance(encoded_link, str):
        print(f"Invalid input: channel_id={channel_id}, encoded_link={encoded_link}")
        return None
    
    try:
        await channels_collection.update_one(
            {"channel_id": channel_id},
            {
                "$set": {
                    "req_encoded_link": encoded_link,
                    "status": "active",
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        return encoded_link
    except Exception as e:
        print(f"Error saving secondary encoded link for channel {channel_id}: {e}")
        return None

async def get_channel_by_encoded_link2(encoded_link: str) -> Optional[int]:
    """Get a channel ID by its secondary encoded link."""
    if not isinstance(encoded_link, str):
        return None
    
    try:
        channel = await channels_collection.find_one({"req_encoded_link": encoded_link, "status": "active"})
        return channel["channel_id"] if channel and "channel_id" in channel else None
    except Exception as e:
        print(f"Error fetching channel by secondary encoded link {encoded_link}: {e}")
        return None

async def save_invite_link(channel_id: int, invite_link: str, is_request: bool) -> bool:
    """Save the current invite link for a channel and its type."""
    if not isinstance(channel_id, int) or not isinstance(invite_link, str):
        print(f"Invalid input: channel_id={channel_id}, invite_link={invite_link}")
        return False
    
    try:
        await channels_collection.update_one(
            {"channel_id": channel_id},
            {
                "$set": {
                    "current_invite_link": invite_link,
                    "is_request_link": is_request,
                    "invite_link_created_at": datetime.utcnow(),
                    "status": "active"
                }
            },
            upsert=True
        )
        return True
    except Exception as e:
        print(f"Error saving invite link for channel {channel_id}: {e}")
        return False

async def get_current_invite_link(channel_id: int) -> Optional[dict]:
    """Get the current invite link and its type for a channel."""
    if not isinstance(channel_id, int):
        return None
    
    try:
        channel = await channels_collection.find_one({"channel_id": channel_id, "status": "active"})
        if channel and "current_invite_link" in channel:
            return {
                "invite_link": channel["current_invite_link"],
                "is_request": channel.get("is_request_link", False)
            }
        return None
    except Exception as e:
        print(f"Error fetching current invite link for channel {channel_id}: {e}")
        return None

async def get_link_creation_time(channel_id: int):
    """Get the creation time of the current invite link for a channel."""
    try:
        channel = await channels_collection.find_one({"channel_id": channel_id, "status": "active"})
        if channel and "invite_link_created_at" in channel:
            return channel["invite_link_created_at"]
        return None
    except Exception as e:
        print(f"Error fetching link creation time for channel {channel_id}: {e}")
        return None

async def add_fsub_channel(channel_id: int, mode: str = "normal") -> bool:
    """Add a channel to the FSub list with a specific mode."""
    if not isinstance(channel_id, int):
        print(f"Invalid channel_id: {channel_id}")
        return False
    
    try:
        await fsub_channels_collection.update_one(
            {'channel_id': channel_id},
            {
                '$set': {
                    'channel_id': channel_id,
                    'mode': mode,
                    'created_at': datetime.utcnow(),
                    'status': 'active'
                }
            },
            upsert=True
        )
        return True
    except Exception as e:
        print(f"Error adding FSub channel {channel_id}: {e}")
        return False

async def remove_fsub_channel(channel_id: int) -> bool:
    """Remove a channel from the FSub list."""
    try:
        result = await fsub_channels_collection.delete_one({'channel_id': channel_id})
        return result.deleted_count > 0
    except Exception as e:
        print(f"Error removing FSub channel {channel_id}: {e}")
        return False

async def get_fsub_channels() -> List[dict]:
    """Get all active FSub channel data."""
    try:
        channels = await fsub_channels_collection.find({'status': 'active'}).to_list(None)
        return channels
    except Exception as e:
        print(f"Error fetching FSub channels: {e}")
        return []

async def get_original_link(channel_id: int) -> Optional[str]:
    """Get the original link stored for a channel (used by /genlink)."""
    if not isinstance(channel_id, int):
        return None
    try:
        channel = await channels_collection.find_one({"channel_id": channel_id, "status": "active"})
        return channel.get("original_link") if channel and "original_link" in channel else None
    except Exception as e:
        print(f"Error fetching original link for channel {channel_id}: {e}")
        return None

async def set_approval_off(channel_id: int, off: bool = True) -> bool:
    """Set approval_off flag for a channel."""
    if not isinstance(channel_id, int):
        print(f"Invalid channel_id: {channel_id}")
        return False
    try:
        await channels_collection.update_one(
            {"channel_id": channel_id},
            {"$set": {"approval_off": off}},
            upsert=True
        )
        return True
    except Exception as e:
        print(f"Error setting approval_off for channel {channel_id}: {e}")
        return False

async def is_approval_off(channel_id: int) -> bool:
    """Check if approval_off flag is set for a channel."""
    if not isinstance(channel_id, int):
        return False
    try:
        channel = await channels_collection.find_one({"channel_id": channel_id})
        return bool(channel and channel.get("approval_off", False))
    except Exception as e:
        print(f"Error checking approval_off for channel {channel_id}: {e}")
        return False
