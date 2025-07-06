#!/usr/bin/env python3
"""
Seed script to populate the database with demo data
"""
import asyncio
import sys
import os
from datetime import datetime
from bson import ObjectId

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import init_db, get_db
from app.core.security import get_password_hash

async def seed_database():
    """Seed the database with demo data"""
    
    # Initialize database connection
    await init_db()
    db = get_db()
    
    print("🌱 Seeding database...")
    
    # Create demo users
    users_data = [
        {
            "email": "alice@example.com",
            "username": "alice",
            "hashed_password": get_password_hash("password123"),
            "avatar": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "email": "bob@example.com",
            "username": "bob",
            "hashed_password": get_password_hash("password123"),
            "avatar": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "email": "charlie@example.com",
            "username": "charlie",
            "hashed_password": get_password_hash("password123"),
            "avatar": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    # Insert users
    user_ids = []
    for user_data in users_data:
        # Check if user already exists
        existing_user = await db.users.find_one({"email": user_data["email"]})
        if existing_user:
            print(f"User {user_data['username']} already exists, skipping...")
            user_ids.append(existing_user["_id"])
        else:
            result = await db.users.insert_one(user_data)
            user_ids.append(result.inserted_id)
            print(f"✅ Created user: {user_data['username']}")
    
    # Create demo channels
    channels_data = [
        {
            "name": "general",
            "description": "General discussion for everyone",
            "created_by": user_ids[0],  # alice
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "name": "random",
            "description": "Random topics and fun discussions",
            "created_by": user_ids[1],  # bob
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "name": "development",
            "description": "Development and technical discussions",
            "created_by": user_ids[2],  # charlie
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    # Insert channels
    channel_ids = []
    for channel_data in channels_data:
        # Check if channel already exists
        existing_channel = await db.channels.find_one({"name": channel_data["name"]})
        if existing_channel:
            print(f"Channel #{channel_data['name']} already exists, skipping...")
            channel_ids.append(existing_channel["_id"])
        else:
            result = await db.channels.insert_one(channel_data)
            channel_ids.append(result.inserted_id)
            print(f"✅ Created channel: #{channel_data['name']}")
    
    # Create demo messages
    messages_data = [
        {
            "content": "Welcome to the general channel! 👋",
            "channel_id": str(channel_ids[0]),
            "user_id": user_ids[0],
            "reactions": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "content": "Hello everyone! How's it going?",
            "channel_id": str(channel_ids[0]),
            "user_id": user_ids[1],
            "reactions": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "content": "Great to be here! 🎉",
            "channel_id": str(channel_ids[0]),
            "user_id": user_ids[2],
            "reactions": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "content": "Anyone up for some random fun? 😄",
            "channel_id": str(channel_ids[1]),
            "user_id": user_ids[1],
            "reactions": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "content": "Let's discuss the latest tech trends! 💻",
            "channel_id": str(channel_ids[2]),
            "user_id": user_ids[2],
            "reactions": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    # Insert messages
    for message_data in messages_data:
        result = await db.messages.insert_one(message_data)
        print(f"✅ Created message in #{message_data['channel_id']}")
    
    print("\n🎉 Database seeding completed!")
    print("\nDemo users created:")
    print("- alice@example.com / password123")
    print("- bob@example.com / password123")
    print("- charlie@example.com / password123")
    print("\nDemo channels created:")
    print("- #general")
    print("- #random")
    print("- #development")

if __name__ == "__main__":
    asyncio.run(seed_database()) 