# services/pytube_downloader.py - Simple YouTube downloader
from pytube import YouTube
import os
import re


def download_youtube_video(url, output_path):
    """
    Download YouTube video using pytube
    """
    try:
        print(f"📥 Downloading with pytube: {url}")

        # Create YouTube object
        yt = YouTube(url, on_progress_callback=None)

        # Get video title
        title = re.sub(r'[^\w\s-]', '', yt.title)[:100]

        # Get the highest resolution stream
        stream = yt.streams.filter(progressive=True, file_extension='mp4').first()

        if not stream:
            # Try adaptive streams if progressive not available
            stream = yt.streams.get_highest_resolution()

        if stream:
            print(f"Downloading: {title}")
            print(f"Resolution: {stream.resolution}")
            print(f"File size: {stream.filesize / 1024 / 1024:.1f} MB")

            # Download
            stream.download(output_path=os.path.dirname(output_path), filename=os.path.basename(output_path))

            return True, title
        else:
            return False, None

    except Exception as e:
        print(f"Pytube error: {e}")
        return False, None