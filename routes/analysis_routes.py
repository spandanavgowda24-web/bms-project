from flask import Blueprint, jsonify
import os, uuid, re

from services.audio_extractor import extract_audio
from services.whisper_service import transcribe_audio
from services.step_detector import detect_steps   # ✅ USE THIS

analysis_bp = Blueprint("analysis_bp", __name__)
UPLOAD_FOLDER = "uploads"


def safe_lang(lang):
    return lang if lang in ["en", "hi", "kn"] else "en"


# 🔥 FAST SUMMARY
def generate_summary(text):
    sentences = re.split(r'[.!?\n]', text)
    return ". ".join([s.strip() for s in sentences if len(s.strip()) > 20][:2])


@analysis_bp.route("/analyze/<filename>", methods=["GET"])
def analyze_file(filename):

    try:
        path = os.path.join(UPLOAD_FOLDER, filename)

        if not os.path.exists(path):
            return jsonify({"error": "File not found"}), 404

        audio_path = os.path.join(UPLOAD_FOLDER, str(uuid.uuid4()) + ".wav")

        # 🔥 FAST AUDIO EXTRACTION
        if not extract_audio(path, audio_path):
            return jsonify({"error": "Audio extraction failed"})

        # 🔥 WHISPER
        result = transcribe_audio(audio_path)

        raw_text = result.get("text", "").strip()
        detected_lang = safe_lang(result.get("language", "en"))

        if not raw_text:
            return jsonify({"error": "Audio not clear"})

        raw_text = raw_text[:1000]   # 🔥 LIMIT FOR SPEED

        print("🌍 LANG:", detected_lang)
        print("TEXT:", raw_text)

        # 🔥 USE NEW STEP DETECTOR
        steps = detect_steps(raw_text, detected_lang)

        # =============================
        # 🔥 STEP RESPONSE (FAST)
        # =============================
        if len(steps) >= 2:

            steps = steps[:5]

            return jsonify({
                "type": "steps",
                "content_en": steps,   # ⚡ NO TRANSLATION (FAST)
                "content_hi": steps,
                "content_kn": steps,
                "language": detected_lang
            })

        # =============================
        # 🔥 SUMMARY (FAST)
        # =============================
        summary = generate_summary(raw_text)

        return jsonify({
            "type": "summary",
            "content_en": summary,
            "content_hi": summary,
            "content_kn": summary,
            "language": detected_lang
        })

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": "Analysis failed"}), 500