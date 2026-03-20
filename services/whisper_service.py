import whisper

print("Loading Whisper model...")

model = whisper.load_model("tiny")

print("Whisper loaded")


def transcribe_audio(audio_path):

    try:

        result = model.transcribe(
            audio_path,
            fp16=False,
            task="transcribe"
        )

        text = result["text"]
        language = result["language"]

        print("Detected language:", language)
        print("Transcribed text:", text)

        return {
            "text": text,
            "language": language
        }

    except Exception as e:

        print("Whisper error:", e)

        return {
            "text": "",
            "language": "unknown"
        }