# routes/link_routes.py - COMPLETE FIX with multiple strategies
from flask import Blueprint, request, jsonify
import os
import uuid
import yt_dlp
from datetime import datetime
import subprocess
import re
from database import db

link_bp = Blueprint("link_bp", __name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "..", "uploads")
UPLOAD_FOLDER = os.path.abspath(UPLOAD_FOLDER)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def is_youtube_url(url):
    """Check if URL is from YouTube"""
    youtube_domains = ['youtube.com', 'youtu.be', 'm.youtube.com', 'www.youtube.com']
    return any(domain in url.lower() for domain in youtube_domains)


def download_with_ytdlp(url, filepath):
    """Try multiple yt-dlp strategies"""

    # Strategy 1: Best quality with modern options
    strategies = [
        {
            'name': 'Modern with cookies',
            'opts': {
                'outtmpl': filepath,
                'format': 'best[ext=mp4]/best',
                'quiet': True,
                'no_warnings': True,
                'ignoreerrors': True,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android', 'web'],
                        'skip': ['hls', 'dash'],
                    }
                }
            }
        },
        {
            'name': 'Low quality (fast)',
            'opts': {
                'outtmpl': filepath,
                'format': 'worst[ext=mp4]/worst',
                'quiet': True,
                'no_warnings': True,
                'ignoreerrors': True,
                'user_agent': 'Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36',
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android'],
                    }
                }
            }
        },
        {
            'name': 'Audio only (smallest)',
            'opts': {
                'outtmpl': filepath,
                'format': 'bestaudio[ext=m4a]/bestaudio',
                'quiet': True,
                'no_warnings': True,
                'ignoreerrors': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '128',
                }],
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android'],
                    }
                }
            }
        }
    ]

    for strategy in strategies:
        try:
            print(f"📡 Trying strategy: {strategy['name']}")
            with yt_dlp.YoutubeDL(strategy['opts']) as ydl:
                info = ydl.extract_info(url, download=True)
                if info and os.path.exists(filepath) and os.path.getsize(filepath) > 10000:
                    print(f"✅ Success with {strategy['name']}")
                    return True, info.get('title', 'Video')
        except Exception as e:
            print(f"❌ Strategy {strategy['name']} failed: {str(e)[:100]}")
            continue

    return False, None


def download_with_youtube_dl(url, filepath):
    """Fallback to youtube-dl if yt-dlp fails"""
    try:
        import youtube_dl

        ydl_opts = {
            'outtmpl': filepath,
            'format': 'best[ext=mp4]/best',
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': True,
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return True, info.get('title', 'Video')
    except Exception as e:
        print(f"❌ youtube-dl failed: {e}")
        return False, None


def download_with_pytube(url, filepath):
    """Another fallback using pytube"""
    try:
        from pytube import YouTube

        yt = YouTube(url)
        # Get the highest resolution stream
        stream = yt.streams.get_highest_resolution()
        if stream:
            stream.download(filename=filepath)
            return True, yt.title
        return False, None
    except Exception as e:
        print(f"❌ pytube failed: {e}")
        return False, None


def get_video_title_from_url(url):
    """Extract video title without downloading"""
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info.get('title', 'Video')[:100]
    except:
        return "Imported Video"


@link_bp.route("/upload-link", methods=["POST"])
def upload_link():
    try:
        data = request.get_json()
        url = data.get('link') or data.get('url')

        if not url:
            return jsonify({"error": "No URL provided"}), 400

        print(f"🔗 Processing link: {url}")

        # Generate unique filename
        download_id = str(uuid.uuid4())[:8]
        filename = f"link_{download_id}.mp4"
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        success = False
        video_title = "Imported Video"

        # Try multiple download methods
        if is_youtube_url(url):
            print("📹 YouTube video detected")

            # Strategy 1: Try yt-dlp
            success, title = download_with_ytdlp(url, filepath)
            if success:
                video_title = title

            # Strategy 2: Try youtube-dl
            if not success:
                print("🔄 Trying youtube-dl...")
                success, title = download_with_youtube_dl(url, filepath)
                if success:
                    video_title = title

            # Strategy 3: Try pytube
            if not success:
                print("🔄 Trying pytube...")
                success, title = download_with_pytube(url, filepath)
                if success:
                    video_title = title
        else:
            # Non-YouTube platforms
            print(f"📱 Non-YouTube platform detected")
            success, title = download_with_ytdlp(url, filepath)
            if success:
                video_title = title

        # If all download methods failed
        if not success or not os.path.exists(filepath):
            print("❌ All download methods failed")
            return jsonify({
                "error": "Download failed. This video may be private, age-restricted, or from an unsupported platform. Try a different video or use file upload instead."
            }), 500

        file_size = os.path.getsize(filepath)
        print(f"✅ Download complete: {file_size / 1024 / 1024:.1f} MB")

        # Get video title if not already set
        if video_title == "Imported Video":
            video_title = get_video_title_from_url(url)

        # Detect platform
        platform = "Unknown"
        if 'youtube.com' in url or 'youtu.be' in url:
            platform = "YouTube"
        elif 'instagram.com' in url:
            platform = "Instagram"
        elif 'facebook.com' in url or 'fb.com' in url:
            platform = "Facebook"
        elif 'twitter.com' in url or 'x.com' in url:
            platform = "Twitter"
        elif 'tiktok.com' in url:
            platform = "TikTok"
        elif 'vimeo.com' in url:
            platform = "Vimeo"

        # Save to database
        user_id = data.get('user_id') or request.headers.get('X-User-Id', 'anonymous')

        video_data = {
            "filename": filename,
            "title": video_title,
            "description": f"Imported from {platform}",
            "category": platform,
            "user_id": user_id,
            "likes": 0,
            "views": 0,
            "comments_count": 0,
            "created_at": datetime.utcnow(),
            "video_type": "link",
            "source_url": url,
            "file_size_mb": round(file_size / 1024 / 1024, 1)
        }

        db.videos.insert_one(video_data)

        return jsonify({
            "success": True,
            "filename": filename,
            "title": video_title,
            "platform": platform,
            "file_size_mb": round(file_size / 1024 / 1024, 1),
            "message": f"Video imported from {platform} successfully"
        })

    except Exception as e:
        print(f"❌ Link processing error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed: {str(e)[:100]}"}), 500