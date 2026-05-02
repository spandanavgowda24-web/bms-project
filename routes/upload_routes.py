# routes/upload_routes.py - WITH VIDEO_TYPE (public/personal)
from flask import Blueprint, request, jsonify
import os
import uuid
from werkzeug.utils import secure_filename
from datetime import datetime
from database import db

upload_bp = Blueprint("upload_bp", __name__)

# Absolute path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "..", "uploads")
UPLOAD_FOLDER = os.path.abspath(UPLOAD_FOLDER)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'mp4', 'mov', 'mkv', 'webm', 'avi'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@upload_bp.route("/upload-video", methods=["POST"])
def upload_video():
    try:
        # Check if file present
        if 'video' not in request.files:
            return jsonify({"error": "No video file"}), 400

        file = request.files['video']

        if file.filename == '':
            return jsonify({"error": "Empty filename"}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid video format. Use mp4, mov, mkv, webm, avi"}), 400

        # Generate unique filename
        ext = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)

        # Save file
        file.save(filepath)

        # Get metadata from form
        title = request.form.get('title', 'Untitled Video')
        description = request.form.get('description', '')
        category = request.form.get('category', 'General')
        user_id = request.form.get('user_id')

        # Get video_type from form (default to 'public' for upload page)
        # 'public' = shows in home_feed, 'personal' = hidden from home_feed
        video_type = request.form.get('video_type', 'public')

        if not user_id:
            user_id = request.headers.get('X-User-Id', 'anonymous')

        # Save to MongoDB with video_type
        video_data = {
            "filename": unique_filename,
            "title": title,
            "description": description,
            "category": category,
            "user_id": user_id,
            "likes": 0,
            "views": 0,
            "comments_count": 0,
            "created_at": datetime.utcnow(),
            "video_type": video_type  # 'public' or 'personal'
        }

        db.videos.insert_one(video_data)

        print(f"✅ Video saved: {unique_filename} by user {user_id} (type: {video_type})")

        return jsonify({
            "success": True,
            "filename": unique_filename,
            "message": "Video uploaded successfully"
        })

    except Exception as e:
        print(f"❌ Upload error: {str(e)}")
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500


@upload_bp.route("/save-meta", methods=["POST"])
def save_metadata():
    """Update video metadata after upload"""
    try:
        data = request.json
        filename = data.get('filename')
        title = data.get('title')
        description = data.get('description')
        category = data.get('category')

        if not filename:
            return jsonify({"error": "No filename"}), 400

        update_data = {}
        if title:
            update_data['title'] = title
        if description:
            update_data['description'] = description
        if category:
            update_data['category'] = category

        if update_data:
            db.videos.update_one(
                {"filename": filename},
                {"$set": update_data}
            )

        return jsonify({"success": True})

    except Exception as e:
        print(f"❌ Save meta error: {str(e)}")
        return jsonify({"error": str(e)}), 500