# services/audio_extractor.py - IMPROVED audio quality
import subprocess
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_audio(video_path: str, audio_path: str) -> str:
    """
    Extract FULL audio with better quality for speech recognition
    """
    try:
        if not os.path.exists(video_path):
            logger.error(f"Video file not found: {video_path}")
            return None

        video_size = os.path.getsize(video_path)
        logger.info(f"Processing video: {video_path} ({video_size} bytes)")

        # Get video duration first
        duration_cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path
        ]

        try:
            duration_result = subprocess.run(duration_cmd, capture_output=True, text=True, timeout=10)
            if duration_result.returncode == 0 and duration_result.stdout:
                duration = float(duration_result.stdout.strip())
                logger.info(f"Video duration: {duration:.2f} seconds")
        except:
            logger.warning("Could not get video duration")

        # Better quality audio extraction for speech
        command = [
            "ffmpeg",
            "-y",
            "-i", video_path,
            "-vn",  # No video
            "-acodec", "pcm_s16le",  # PCM 16-bit
            "-ac", "1",  # Mono
            "-ar", "16000",  # 16kHz (optimal for Whisper)
            "-af", "volume=2.0",  # Boost volume
            "-threads", "2",
            audio_path
        ]

        logger.info("Extracting full audio with volume boost...")

        # Windows hide window
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE

        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=180,
            startupinfo=startupinfo
        )

        if result.returncode != 0:
            error_msg = result.stderr.decode('utf-8', errors='ignore')[:200]
            logger.error(f"FFmpeg error: {error_msg}")
            return None

        # Verify output
        if os.path.exists(audio_path):
            audio_size = os.path.getsize(audio_path)
            if audio_size > 5000:
                logger.info(f"✅ Audio extracted: {audio_size} bytes")
                return audio_path
            else:
                logger.error(f"Audio file too small: {audio_size} bytes")
                return None
        else:
            logger.error("Audio file not created")
            return None

    except subprocess.TimeoutExpired:
        logger.error("Audio extraction timed out")
        return None
    except Exception as e:
        logger.error(f"Audio extraction error: {str(e)}")
        return None