import subprocess


def extract_audio(video_path, audio_path):

    try:

        command = [
            "ffmpeg",
            "-y",
            "-i", video_path,
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            audio_path
        ]

        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        print("Audio extracted successfully")

        return audio_path

    except Exception as e:

        print("Audio extraction error:", e)

        return None