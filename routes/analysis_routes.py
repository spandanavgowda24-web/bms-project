from flask import Blueprint, jsonify, request
from services.tts_service import generate_speech
import os, uuid, re

from services.audio_extractor import extract_audio
from services.whisper_service import transcribe_audio

analysis_bp = Blueprint("analysis_bp", __name__)
UPLOAD_FOLDER = "uploads"


# 🔥 IMPROVED STEP DETECTOR (BALANCED)
def ai_detect_steps(text):

    sentences = re.split(
        r'[.!?\n]|'
        r'\b(?:then|next|after that|and then|now|finally)\b',
        text,
        flags=re.IGNORECASE
    )

    steps = []

    action_words = [
        "add","mix","apply","use","start","take","put",
        "open","click","press","select","install","run",
        "create","fill","pour","heat","cook","insert",
        "connect","cut","wash","boil","remove","combine"
    ]

    for s in sentences:
        line = s.strip()
        lower = line.lower()

        # ❌ ignore too small
        if len(line) < 12:
            continue

        # ❌ remove intro only
        if lower.startswith(("hi", "hello", "welcome", "today", "so guys")):
            continue

        # ✅ allow natural instructions also
        if (
            any(w in lower for w in action_words)
            or lower.startswith(("first", "next", "then", "after"))
            or lower.startswith(("i use", "you can", "now you", "let's"))
        ):
            steps.append(line.capitalize())

    # 🔥 remove duplicates
    final_steps = []
    for s in steps:
        if s not in final_steps:
            final_steps.append(s)

    return final_steps


@analysis_bp.route("/analyze/<filename>", methods=["GET"])
def analyze_file(filename):

    try:
        path = os.path.join(UPLOAD_FOLDER, filename)

        if not os.path.exists(path):
            return jsonify({"error": "File not found"}), 404

        audio_path = os.path.join(UPLOAD_FOLDER, str(uuid.uuid4()) + ".wav")

        try:
            extract_audio(path, audio_path)
        except:
            audio_path = path

        result = transcribe_audio(audio_path)
        raw_text = result.get("text", "")

        if not raw_text or len(raw_text.strip()) < 10:
            return jsonify({"error": "No speech detected"}), 400

        # 🔥 LIMIT (performance)
        raw_text = raw_text[:800]

        print("TEXT:", raw_text)

        steps = ai_detect_steps(raw_text)

        print("STEPS:", steps)

        # 🔥 COUNT SENTENCES
        total_sentences = len([s for s in re.split(r'[.!?\n]', raw_text) if s.strip()])

        print("TOTAL SENTENCES:", total_sentences)

        # 🔥 SMART DECISION (FINAL FIX)
        if (
            steps
            and len(steps) >= 2
            and len(steps) >= max(2, int(total_sentences * 0.2))
        ):

            steps = steps[:6]

            audio_files = []
            for s in steps:
                f = generate_speech(s, "en")
                if f:
                    audio_files.append(f)

            return jsonify({
                "type": "steps",
                "content": steps,
                "audio": audio_files,
                "language": "en"
            })

        # 🔥 SUMMARY (BETTER LENGTH)
        summary = raw_text[:500]

        return jsonify({
            "type": "summary",
            "content": summary,
            "language": "en"
        })

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": "Analysis failed"}), 500