from pymongo import MongoClient
from config import MONGO_URI, DB_NAME

# Create MongoDB connection
client = MongoClient(MONGO_URI)

# Select database
db = client[DB_NAME]

# Collections
users_collection = db["users"]
uploads_collection = db["uploads"]
analysis_collection = db["analysis"]
videos_collection = db["videos"]

# Optional: function to test DB connection
def test_connection():
    try:
        client.admin.command("ping")
        print("MongoDB connected successfully")
    except Exception as e:
        print("MongoDB connection error:", e)