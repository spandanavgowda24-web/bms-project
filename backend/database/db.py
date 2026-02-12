import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Get Mongo URI from .env
MONGO_URI = os.getenv("MONGO_URI")

# Create Mongo Client
client = MongoClient(MONGO_URI)

# Select Database
db = client["project_db"]

# Collections
users_collection = db["users"]
sessions_collection = db["sessions"]
interactions_collection = db["interactions"]
responses_collection = db["responses"]
