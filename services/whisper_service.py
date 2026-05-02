# services/whisper_service.py - IMPROVED
import whisper
import os
import re

print("🔄 Loading Whisper model...")
model = whisper.load_model("base")
print("✅ Whisper loaded")


def transcribe_audio(audio_path):
    """
    Transcribe audio with better error handling
    """
    try:
        if not audio_path or not os.path.exists(audio_path):
            print("❌ Audio file not found")
            return {"text": "", "language": "en"}

        file_size = os.path.getsize(audio_path)
        print(f"🎧 Audio size: {file_size} bytes")

        if file_size < 5000:
            print("❌ Audio file too small")
            return {"text": "", "language": "en"}

        # Transcribe with standard settings
        result = model.transcribe(
            audio_path,
            fp16=False,
            language=None,  # Auto-detect
            task="transcribe",
            verbose=False,
            temperature=0.0
        )

        raw_text = result.get("text", "").strip()
        detected_lang = result.get("language", "en")

        # Clean text
        raw_text = re.sub(r'\s+', ' ', raw_text).strip()

        print(f"🌍 Detected language: {detected_lang}")
        print(f"📝 Transcript: {raw_text[:200]}...")

        # If text is too short, try translating to English
        if len(raw_text) < 30 and detected_lang != "en":
            print("🔄 Short transcript, trying translation...")
            result_trans = model.transcribe(
                audio_path,
                fp16=False,
                task="translate",
                verbose=False
            )
            translated_text = result_trans.get("text", "").strip()
            if len(translated_text) > len(raw_text):
                raw_text = translated_text
                detected_lang = "en"
                print(f"📝 Translated: {raw_text[:200]}...")

        return {
            "text": raw_text,
            "language": detected_lang
        }

    except Exception as e:
        print(f"❌ Whisper error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"text": "", "language": "en"}