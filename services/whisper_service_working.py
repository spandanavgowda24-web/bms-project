import whisper
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_model = None


def get_model():
    global _model
    if _model is None:
        logger.info("Loading Whisper model (tiny)...")
        _model = whisper.load_model("tiny")
        logger.info("✅ Model loaded")
    return _model


def transcribe_audio(audio_path: str) -> dict:
    try:
        if not os.path.exists(audio_path):
            return {"text": "Audio file not found", "language": "en"}

        file_size = os.path.getsize(audio_path)
        if file_size < 1000:
            return {"text": "Audio file too small", "language": "en"}

        logger.info(f"Transcribing: {os.path.basename(audio_path)}")

        model = get_model()
        result = model.transcribe(audio_path, fp16=False)

        text = result.get("text", "").strip()
        language = result.get("language", "en")

        if not text:
            return {"text": "No speech detected", "language": language}

        logger.info(f"✅ Transcription: {len(text)} chars")
        return {"text": text, "language": language}

    except Exception as e:
        logger.error(f"Error: {e}")
        return {"text": "Transcription failed", "language": "en"}