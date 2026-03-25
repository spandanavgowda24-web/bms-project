import subprocess
import os

def extract_audio(video_path, audio_path):

    try:
        if not os.path.exists(video_path):
            print("❌ Video not found")
            return None

        command = [
            "ffmpeg",
            "-y",
            "-i", video_path,

            # 🔥 KEEP FULL AUDIO (no trimming)
            "-vn",

            # 🔥 BEST FORMAT FOR WHISPER
            "-acodec", "pcm_s16le",
            "-ac", "1",
            "-ar", "16000",

            # 🔥 LIGHT CLEANING ONLY (DO NOT OVERFILTER)
            "-af",
            "dynaudnorm",

            audio_path
        ]

        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        print("FFmpeg stderr:", result.stderr.decode())

        if not os.path.exists(audio_path):
            print("❌ Audio not created")
            return None

        size = os.path.getsize(audio_path)

        if size < 10000:
            print("❌ Audio too small:", size)
            return None

        print("✅ CLEAN AUDIO READY:", size)

        return audio_path

    except Exception as e:
        print("❌ Audio extraction error:", e)
        return None