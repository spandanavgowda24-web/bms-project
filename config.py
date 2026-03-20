import os

MONGO_URI = "mongodb://localhost:27017"

DB_NAME = "ai_voice_system"

JWT_SECRET = "supersecretkey123456"
JWT_ALGORITHM = "HS256"

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)