# test_audio.py - Run this to test audio extraction
import os
import subprocess


def test_ffmpeg():
    result = subprocess.run(["ffmpeg", "-version"], capture_output=True)
    if result.returncode == 0:
        print("✅ FFmpeg is installed")
        return True
    else:
        print("❌ FFmpeg is NOT installed")
        return False


def test_audio_extraction(video_path):
    from services.audio_extractor import extract_audio

    audio_path = "test_output.wav"
    result = extract_audio(video_path, audio_path)

    if result and os.path.exists(audio_path):
        size = os.path.getsize(audio_path)
        print(f"✅ Audio extracted: {size} bytes")
        os.remove(audio_path)
        return True
    else:
        print("❌ Audio extraction failed")
        return False


if __name__ == "__main__":
    test_ffmpeg()