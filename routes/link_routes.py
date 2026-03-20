from flask import Blueprint, request, jsonify
import os
import uuid
import yt_dlp

from services.link_processor import clean_url

link_bp = Blueprint("link_bp", __name__)

UPLOAD_FOLDER = "uploads"


# 🔥 PROGRESS HOOK
def progress_hook(d):

    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '0%')
        speed = d.get('_speed_str', '0KB/s')
        print(f"Downloading: {percent} at {speed}")

    elif d['status'] == 'finished':
        print("Download completed!")


@link_bp.route("/upload-link", methods=["POST"])
def upload_link():

    try:

        data = request.get_json()
        url = data.get("link")

        if not url:
            return jsonify({"error": "No link provided"}), 400

        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        # ✅ CLEAN URL
        cleaned_url = clean_url(url)

        if not cleaned_url:
            return jsonify({
                "error": "Invalid link. Paste YouTube or Instagram link only."
            }), 400

        print("Cleaned URL:", cleaned_url)

        filename = str(uuid.uuid4()) + ".mp4"
        file_path = os.path.join(UPLOAD_FOLDER, filename)

        # 🔥 OPTIMIZED yt-dlp SETTINGS
        ydl_opts = {
            "format": "best[ext=mp4]/best",   # faster + compatible
            "outtmpl": file_path,
            "noplaylist": True,
            "quiet": False,                  # show logs
            "progress_hooks": [progress_hook],  # 🔥 progress
            "concurrent_fragment_downloads": 4,  # 🔥 speed boost
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([cleaned_url])

        return jsonify({
            "filename": filename
        })

    except Exception as e:

        print("Link processing error:", str(e))

        return jsonify({
            "error": "Failed to process link"
        }), 500