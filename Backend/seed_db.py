import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import certifi
from datetime import datetime

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "skillsetu_db"

# Sample Data to make the dashboard look "alive"
MOCK_USERS = [
    {"name": "Aarav Sharma", "state": "Uttar Pradesh", "skill": "Electrician", "score": 85, "result": "PASS"},
    {"name": "Priya Patel", "state": "Gujarat", "skill": "Plumber", "score": 72, "result": "PASS"},
    {"name": "Ishan Nair", "state": "Kerala", "skill": "Welder", "score": 45, "result": "FAIL"},
    {"name": "Ananya Das", "state": "West Bengal", "skill": "Carpenter", "score": 92, "result": "PASS"},
    {"name": "Vikram Singh", "state": "Maharashtra", "skill": "Electrician", "score": 78, "result": "PASS"},
    {"name": "Sanya Malhotra", "state": "Delhi", "skill": "Mason", "score": 65, "result": "FAIL"},
    {"name": "Karthik Raja", "state": "Tamil Nadu", "skill": "Plumber", "score": 88, "result": "PASS"},
    {"name": "Rahul Verma", "state": "Bihar", "skill": "Welder", "score": 30, "result": "FAIL"},
    {"name": "Sneha Reddy", "state": "Telangana", "skill": "Carpenter", "score": 81, "result": "PASS"},
    {"name": "Arjun Meena", "state": "Rajasthan", "skill": "Mason", "score": 74, "result": "PASS"},
]

async def seed_database():
    print("Connecting to MongoDB Atlas...")
    client = AsyncIOMotorClient(MONGO_URI, tlsCAFile=certifi.where())
    db = client[DB_NAME]
    
    # Clear existing data so we start fresh
    print("🧹 Cleaning existing users...")
    await db.users.delete_many({})

    print(f" Injecting {len(MOCK_USERS)} mock workers...")
    
    for i, mock in enumerate(MOCK_USERS):
        user_doc = {
            "clerk_id": f"user_mock_{i}",
            "name": mock["name"],
            "state": mock["state"],
            "skills": [{
                "skill_name": mock["skill"],
                "score": mock["score"],
                "result": mock["result"],
                "badges": ["AI Verified", "Safety Cleared"] if mock["result"] == "PASS" else ["Beginner"]
            }],
            "activity_log": [{
                "name": mock["name"],
                "skill": mock["skill"],
                "result": mock["result"],
                "date": datetime.now().strftime("%Y-%m-%d"),
                "timestamp": datetime.now()
            }]
        }
        await db.users.insert_one(user_doc)

    print("Database successfully seeded!")
    print("Now check your Dashboard and Heatmap!")
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_database())