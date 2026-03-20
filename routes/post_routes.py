from flask import Blueprint, request, jsonify
import os
import uuid
from datetime import datetime

from database import videos_collection
from services.audio_extractor import extract_audio
from services.whisper_service import transcribe_audio

post_bp = Blueprint("post", __name__)

UPLOAD_FOLDER = "uploads"

ALLOWED_VIDEO_EXTENSIONS = {"mp4", "mov", "avi", "mkv", "webm"}


def allowed_video(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_VIDEO_EXTENSIONS


@post_bp.route("/upload-post", methods=["POST"])
def upload_post():

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    title = request.form.get("title")
    description = request.form.get("description")
    category = request.form.get("category")
    user_id = request.form.get("user_id")

    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    # Reject audio
    if not allowed_video(file.filename):
        return jsonify({
            "error": "Only instructional videos are allowed"
        }), 400

    filename = str(uuid.uuid4()) + "_" + file.filename
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    file.save(filepath)

    # Extract audio
    audio_path = filepath + ".wav"
    extract_audio(filepath, audio_path)

    # Speech to text
    result = transcribe_audio(audio_path)

    text = result["text"]
    language = result["language"]

    # Detect steps
    steps = detect_steps(text, language)

    if len(steps) < 2:
        return jsonify({
            "error": "This video does not appear to contain instructions"
        }), 400

    # Save in MongoDB
    video_data = {

        "title": title,
        "description": description,
        "category": category,

        "filename": filename,

        "video_type": "normal",

        "uploaded_by": user_id,

        "views": 0,
        "likes": 0,
        "comments_count": 0,

        "created_at": datetime.now()
    }

    videos_collection.insert_one(video_data)

    return jsonify({
        "message": "Instruction video uploaded successfully"
    })