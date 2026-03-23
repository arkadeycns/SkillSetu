import os
import certifi 
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Force Python to find the .env file in the parent directory (Backend folder)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR)
env_path = os.path.join(BASE_DIR, ".env")

load_dotenv(dotenv_path=env_path)

print(f"\n=== DATABASE CONNECTION CHECK ===")
print(f"Looking for .env file at: {env_path}")
MONGO_URI = os.getenv("MONGO_URI")

if MONGO_URI:
    # Print just the prefix so we don't leak your password in the console
    print(f"MONGO_URI found: {MONGO_URI[:20]}...")
else:
    print("MONGO_URI IS MISSING! Falling back to localhost.")
    MONGO_URI = "mongodb://localhost:27017"
print("===================================\n")

DB_NAME = "skillsetu_db"

class Database:
    client: AsyncIOMotorClient = None
    db = None

db_instance = Database()

async def connect_to_mongo():
    print("[startup] Connecting to MongoDB...")
    
   
    db_instance.client = AsyncIOMotorClient(
        MONGO_URI, 
        tls=True, 
        tlsAllowInvalidCertificates=True 
    )
    db_instance.db = db_instance.client[DB_NAME]
    
    print("[startup] Connected to MongoDB successfully!")

async def close_mongo_connection():
    print("[shutdown] Closing MongoDB connection...")
    if db_instance.client:
        db_instance.client.close()

def get_db():
    return db_instance.db