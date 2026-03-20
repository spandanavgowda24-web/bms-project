from flask import Blueprint, request, jsonify
from database import db
import uuid
import os

video_bp = Blueprint("video_bp", __name__)

UPLOAD_FOLDER = "uploads"


@video_bp.route("/upload-video", methods=["POST"])
def upload_video():

    try:

        title = request.form.get("title")
        description = request.form.get("description")
        category = request.form.get("category")

        user_id = request.form.get("user_id") or "demo_user"

        if "video" not in request.files:
            return jsonify({"error": "No video file"}), 400

        video_file = request.files["video"]

        if video_file.filename == "":
            return jsonify({"error": "Empty filename"}), 400


        allowed_extensions = [".mp4", ".mov", ".mkv", ".webm"]

        ext = os.path.splitext(video_file.filename)[1].lower()

        if ext not in allowed_extensions:
            return jsonify({
                "error": "Only video files allowed for public uploads"
            }), 400


        filename = str(uuid.uuid4()) + "_" + video_file.filename

        filepath = os.path.join(UPLOAD_FOLDER, filename)

        video_file.save(filepath)

        video_data = {
            "title": title,
            "description": description,
            "category": category,
            "filename": filename,
            "user_id": user_id,
            "views": 0,
            "likes": 0,
            "comments": []
        }

        db.videos.insert_one(video_data)

        return jsonify({
            "message": "Video uploaded successfully"
        })

    except Exception as e:

        print("Upload video error:", e)

        return jsonify({"error": "Upload failed"}), 500


@video_bp.route("/videos", methods=["GET"])
def get_videos():

    videos_cursor = db.videos.find()

    videos = []

    for v in videos_cursor:

        videos.append({
            "title": v.get("title"),
            "description": v.get("description"),
            "category": v.get("category"),
            "filename": v.get("filename"),
            "user_id": v.get("user_id", ""),
            "views": v.get("views", 0),
            "likes": v.get("likes", 0),
            "comments": v.get("comments", [])
        })

    return jsonify(videos)