
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")

client = MongoClient(MONGO_URL)

db = client["skillset"]

users_collection = db["users"]
skills_collection = db["skills"]
 
print("✅ MongoDB connected successfully")