# routes/video_routes.py - CLEAN VERSION (no duplicate functions)
from flask import Blueprint, request, jsonify
from database import db
import os
from datetime import datetime

video_bp = Blueprint("video_bp", __name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "..", "uploads")
UPLOAD_FOLDER = os.path.abspath(UPLOAD_FOLDER)


# ===================== VIEWS =====================
@video_bp.route("/increment-views/<filename>", methods=["POST"])
def increment_views(filename):
    try:
        db.videos.update_one({"filename": filename}, {"$inc": {"views": 1}})
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@video_bp.route("/like-video", methods=["POST"])
def like_video():
    try:
        data = request.json
        user_id = data.get("user_id")
        filename = data.get("filename")

        existing = db.likes.find_one({"user_id": user_id, "filename": filename})

        if existing:
            db.likes.delete_one({"_id": existing["_id"]})
            db.videos.update_one({"filename": filename}, {"$inc": {"likes": -1}})
            return jsonify({"message": "unliked"})
        else:
            db.likes.insert_one({"user_id": user_id, "filename": filename})
            db.videos.update_one({"filename": filename}, {"$inc": {"likes": 1}})
            return jsonify({"message": "liked"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@video_bp.route("/add-comment", methods=["POST"])
def add_comment():
    try:
        data = request.json
        filename = data.get("filename")
        user_id = data.get("user_id")
        text = data.get("text")

        # Insert comment
        db.comments.insert_one({
            "filename": filename,
            "user_id": user_id,
            "text": text,
            "created_at": datetime.utcnow()
        })

        # Increment comments_count in videos collection
        db.videos.update_one(
            {"filename": filename},
            {"$inc": {"comments_count": 1}}
        )

        return jsonify({"success": True})
    except Exception as e:
        print(f"❌ Add comment error: {e}")
        return jsonify({"error": str(e)}), 500


@video_bp.route("/get-comments/<filename>", methods=["GET"])
def get_comments(filename):
    try:
        comments = list(db.comments.find(
            {"filename": filename},
            {"_id": 0}
        ).sort("created_at", -1).limit(20))
        return jsonify(comments)
    except Exception as e:
        return jsonify([])


@video_bp.route("/videos", methods=["GET"])
def get_videos():
    """
    Get PUBLIC videos only (for home feed)
    """
    try:
        page = int(request.args.get("page", 1))
        limit = 12
        skip = (page - 1) * limit

        videos_cursor = db.videos.find({
            "$or": [
                {"video_type": "public"},
                {"video_type": {"$exists": False}}
            ]
        }).sort("created_at", -1).skip(skip).limit(limit)

        videos = []
        for v in videos_cursor:
            filename = v.get("filename")
            if filename and os.path.exists(os.path.join(UPLOAD_FOLDER, filename)):
                videos.append({
                    "filename": filename,
                    "title": v.get("title", "Untitled"),
                    "likes": v.get("likes", 0),
                    "views": v.get("views", 0),
                    "description": v.get("description", ""),
                    "category": v.get("category", ""),
                    "user_id": v.get("user_id", "unknown"),
                    "comments_count": v.get("comments_count", 0),
                    "created_at": str(v.get("created_at", datetime.utcnow()))
                })

        return jsonify(videos)

    except Exception as e:
        print(f"❌ Fetch error: {e}")
        return jsonify([])


@video_bp.route("/my-videos", methods=["GET"])
def get_my_videos():
    """
    Get ALL videos for a specific user (both public and personal)
    """
    try:
        user_id = request.args.get("user_id")

        if not user_id or user_id == 'null' or user_id == 'undefined':
            return jsonify({"error": "User ID required"}), 400

        videos_cursor = db.videos.find({"user_id": user_id}).sort("created_at", -1)

        videos = []
        for v in videos_cursor:
            filename = v.get("filename")
            if filename:
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                videos.append({
                    "filename": filename,
                    "title": v.get("title", "Untitled"),
                    "likes": v.get("likes", 0),
                    "views": v.get("views", 0),
                    "description": v.get("description", ""),
                    "comments_count": v.get("comments_count", 0),
                    "video_type": v.get("video_type", "public"),
                    "exists": os.path.exists(filepath)
                })

        return jsonify(videos)

    except Exception as e:
        print(f"❌ My videos error: {e}")
        return jsonify([])


@video_bp.route("/delete-video/<filename>", methods=["DELETE"])
def delete_video(filename):
    try:
        user_id = request.args.get("user_id")

        video = db.videos.find_one({"filename": filename})

        if not video:
            return jsonify({"error": "Video not found"}), 404

        if video.get("user_id") != user_id:
            return jsonify({"error": "Not authorized to delete this video"}), 403

        # Delete file
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(filepath):
            os.remove(filepath)

        # Delete from database
        db.videos.delete_one({"filename": filename})

        # Delete associated analysis cache
        db.analysis.delete_many({"filename": filename})

        # Delete associated likes
        db.likes.delete_many({"filename": filename})

        # Delete associated comments
        db.comments.delete_many({"filename": filename})

        return jsonify({"success": True, "message": "Video deleted"})

    except Exception as e:
        print(f"❌ Delete error: {e}")
        return jsonify({"error": "Delete failed"}), 500


@video_bp.route("/recommended", methods=["GET"])
def recommended():
    """
    Get recommended PUBLIC videos only
    """
    try:
        videos_cursor = db.videos.find({
            "$or": [
                {"video_type": "public"},
                {"video_type": {"$exists": False}}
            ]
        }).sort("likes", -1).limit(10)

        videos = []
        for v in videos_cursor:
            videos.append({
                "filename": v.get("filename"),
                "title": v.get("title", "Untitled"),
                "likes": v.get("likes", 0),
                "views": v.get("views", 0)
            })

        return jsonify(videos)

    except Exception as e:
        print(f"❌ RECOMMEND ERROR:", e)
        return jsonify([])


@video_bp.route("/search", methods=["GET"])
def search_videos():
    """
    Search ONLY public videos
    """
    try:
        query = request.args.get("q", "")

        results = db.videos.find({
            "$and": [
                {"title": {"$regex": query, "$options": "i"}},
                {"$or": [
                    {"video_type": "public"},
                    {"video_type": {"$exists": False}}
                ]}
            ]
        })

        videos = []
        for v in results:
            videos.append({
                "filename": v.get("filename"),
                "title": v.get("title", "Untitled"),
                "likes": v.get("likes", 0),
                "views": v.get("views", 0),
                "comments_count": v.get("comments_count", 0)
            })

        return jsonify(videos)

    except Exception as e:
        print(f"❌ SEARCH ERROR:", e)
        return jsonify([])