#!/usr/bin/env python3
"""
Database setup script for Akan Health Assistant
"""

import asyncio
import sys
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.core.auth import get_password_hash

async def setup_mongodb():
    """Setup MongoDB collections and indexes"""
    print("Setting up MongoDB...")
    
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        db = client.akan_health_db
        
        # Test connection
        await client.admin.command('ping')
        print("✅ Connected to MongoDB")
        
        # Create collections with indexes
        collections = [
            {
                "name": "users",
                "indexes": [
                    ("email", 1),  # Unique index will be created separately
                    ("created_at", -1),
                    ("preferred_language", 1)
                ]
            },
            {
                "name": "health_queries",
                "indexes": [
                    ("user_id", 1),
                    ("created_at", -1),
                    ("query_language", 1),
                    ("response_language", 1)
                ]
            },
            {
                "name": "query_logs",
                "indexes": [
                    ("timestamp", -1),
                    ("user_id", 1),
                    ("query_id", 1),
                    ("type", 1)
                ]
            },
            {
                "name": "error_logs",
                "indexes": [
                    ("timestamp", -1),
                    ("user_id", 1),
                    ("type", 1)
                ]
            }
        ]
        
        for collection_info in collections:
            collection = db[collection_info["name"]]
            
            # Create indexes
            for index in collection_info["indexes"]:
                if isinstance(index, tuple):
                    await collection.create_index([index])
                else:
                    await collection.create_index(index)
            
            print(f"✅ Created collection: {collection_info['name']}")
        
        # Create unique index for users email
        await db.users.create_index("email", unique=True)
        print("✅ Created unique email index")
        
        print("✅ MongoDB setup completed")
        
        client.close()
        
    except Exception as e:
        print(f"❌ MongoDB setup failed: {e}")
        raise

async def create_sample_data():
    """Create sample data for testing"""
    print("Creating sample data...")
    
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        db = client.akan_health_db
        
        # Create admin user
        admin_email = "admin@akanhealth.com"
        existing_admin = await db.users.find_one({"email": admin_email})
        
        if not existing_admin:
            admin_user = {
                "_id": "admin-user-id-123",
                "email": admin_email,
                "hashed_password": get_password_hash("admin123"),
                "full_name": "Admin User",
                "preferred_language": "en",
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            await db.users.insert_one(admin_user)
            print(f"✅ Created admin user: {admin_email}")
        else:
            print(f"✅ Admin user already exists: {admin_email}")
        
        # Create test users
        test_users = [
            {
                "_id": "test-user-id-456",
                "email": "test@example.com",
                "hashed_password": get_password_hash("testpass123"),
                "full_name": "Test User",
                "preferred_language": "en",
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "_id": "akan-user-id-789",
                "email": "akan@example.com",
                "hashed_password": get_password_hash("akanpass123"),
                "full_name": "Akan User",
                "preferred_language": "ak",
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        for user_data in test_users:
            existing_user = await db.users.find_one({"email": user_data["email"]})
            if not existing_user:
                await db.users.insert_one(user_data)
                print(f"✅ Created test user: {user_data['email']}")
        
        print("✅ Sample data created")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Sample data creation failed: {e}")
        raise

async def main():
    """Main setup function"""
    print("🚀 Setting up Akan Health Assistant Database...")
    
    try:
        # Setup MongoDB
        await setup_mongodb()
        
        # Create sample data
        await create_sample_data()
        
        print("✅ Database setup completed successfully!")
        print("\nDefault credentials:")
        print("Admin: admin@akanhealth.com / admin123")
        print("Test User: test@example.com / testpass123")
        print("Akan User: akan@example.com / akanpass123")
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
