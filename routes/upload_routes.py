from flask import Blueprint, request, jsonify
import os
import uuid

upload_bp = Blueprint("upload", __name__)

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Allowed formats for voice assistant upload
ALLOWED_EXTENSIONS = {
    "mp4", "mov", "avi", "mkv", "webm",  # video
    "mp3", "wav", "m4a", "ogg", "webm"   # audio
}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@upload_bp.route("/upload-media", methods=["POST"])
def upload_media():

    if "file" not in request.files:
        return jsonify({"error": "No file received"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    # Check allowed file types
    if not allowed_file(file.filename):
        return jsonify({
            "error": "Unsupported file format"
        }), 400

    filename = str(uuid.uuid4()) + "_" + file.filename
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    file.save(filepath)

    print("FILE SAVED:", filename)

    return jsonify({
        "message": "Upload successful",
        "filename": filename
    })