# routes/analysis_routes.py - FIXED (Better step vs story detection)
from flask import Blueprint, jsonify
import os
import uuid
import re
from database import db
from services.audio_extractor import extract_audio
from services.whisper_service import transcribe_audio
from services.step_detector import detect_steps, generate_summary
from services.translator import translate_list

analysis_bp = Blueprint("analysis_bp", __name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "..", "uploads")
UPLOAD_FOLDER = os.path.abspath(UPLOAD_FOLDER)


def safe_lang(lang):
    return lang if lang in ["en", "hi", "kn"] else "en"


def is_story_content(text):
    """Check if the content is a story (not instructional)"""
    story_keywords = [
        'once upon a time', 'moral', 'fairy tale', 'story', 'happily ever after',
        'child found', 'stone said', 'magic', 'wish came true', 'moral of the story',
        'एक बार की बात है', 'कहानी', 'नैतिक', 'ಒಂದಾನೊಂದು ಕಾಲದಲ್ಲಿ', 'ಕಥೆ', 'ನೀತಿ'
    ]
    text_lower = text.lower()
    for keyword in story_keywords:
        if keyword in text_lower:
            return True
    return False


def has_step_keywords(text):
    """Check if text has step-by-step indicators"""
    step_keywords = [
        'first', 'then', 'next', 'after', 'finally', 'step', 'how to',
        'पहले', 'फिर', 'अगला', 'बाद', 'अंत में', 'चरण',
        'ಮೊದಲು', 'ನಂತರ', 'ಮುಂದೆ', 'ನಂತರ', 'ಕೊನೆಯಲ್ಲಿ', 'ಹಂತ'
    ]
    text_lower = text.lower()
    for keyword in step_keywords:
        if keyword in text_lower:
            return True
    return False


def has_action_verbs(text):
    """Check if text has instructional action verbs"""
    action_verbs = [
        'add', 'pour', 'mix', 'stir', 'boil', 'cook', 'heat', 'cut', 'chop',
        'open', 'click', 'go', 'select', 'press', 'type', 'save', 'delete',
        'डालें', 'मिलाएं', 'पकाएं', 'काटें', 'खोलें', 'दबाएं',
        'ಸೇರಿಸಿ', 'ಬೆರೆಸಿ', 'ಬೇಯಿಸಿ', 'ಕತ್ತರಿಸಿ', 'ತೆರೆಯಿರಿ', 'ಒತ್ತಿ'
    ]
    text_lower = text.lower()
    for verb in action_verbs:
        if verb in text_lower:
            return True
    return False


@analysis_bp.route("/analyze/<filename>", methods=["GET"])
def analyze_file(filename):
    audio_path = None
    try:
        print(f"\n🔍 Analyzing: {filename}")

        # Check cache
        existing = db.analysis.find_one({"filename": filename})
        if existing and "result" in existing:
            print("✅ Using cached result")
            return jsonify(existing["result"])

        video_path = os.path.join(UPLOAD_FOLDER, filename)

        if not os.path.exists(video_path):
            return jsonify({
                "type": "error",
                "content_en": "Video file not found"
            })

        # Extract audio
        audio_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4().hex}.wav")

        print("🎵 Extracting audio...")
        if not extract_audio(video_path, audio_path):
            return jsonify({
                "type": "error",
                "content_en": "Could not extract audio from video"
            })

        # Transcribe
        print("🎤 Transcribing with Whisper...")
        result = transcribe_audio(audio_path)

        raw_text = result.get("text", "").strip()
        detected_lang = safe_lang(result.get("language", "en"))

        print(f"📝 Transcript: {raw_text[:300]}...")
        print(f"📏 Length: {len(raw_text)} chars")

        if not raw_text or len(raw_text) < 20:
            return jsonify({
                "type": "error",
                "content_en": "No clear speech detected. Please ensure your video has clear audio."
            })

        # Check if content is a story
        is_story = is_story_content(raw_text)
        has_steps = has_step_keywords(raw_text)
        has_actions = has_action_verbs(raw_text)

        # Detect steps
        steps = detect_steps(raw_text, detected_lang)
        print(f"📊 Detected {len(steps)} steps")
        print(f"📖 Is story: {is_story}, Has step keywords: {has_steps}, Has actions: {has_actions}")

        # For stories - return summary instead of steps
        if is_story and len(steps) <= 2 and not has_steps:
            summary = generate_summary(raw_text, steps)
            response = {
                "type": "summary",
                "content_en": summary,
                "content_hi": summary,
                "content_kn": summary,
                "language": detected_lang
            }
            print(f"📖 Returning summary (detected as story content)")
        # For instructional content - return steps
        elif len(steps) >= 1 and (has_steps or has_actions or len(steps) >= 2):
            steps_hi = translate_list(steps, "hi") if steps else []
            steps_kn = translate_list(steps, "kn") if steps else []

            response = {
                "type": "steps",
                "content_en": steps,
                "content_hi": steps_hi if steps_hi else steps,
                "content_kn": steps_kn if steps_kn else steps,
                "language": detected_lang,
                "step_count": len(steps)
            }
            print(f"✅ Returning {len(steps)} steps (instructional content)")
        else:
            # Fallback to summary
            summary = generate_summary(raw_text, steps)
            response = {
                "type": "summary",
                "content_en": summary,
                "content_hi": summary,
                "content_kn": summary,
                "language": detected_lang
            }
            print(f"📄 Returning summary (fallback)")

        # Cache the result
        db.analysis.insert_one({
            "filename": filename,
            "result": response
        })

        return jsonify(response)

    except Exception as e:
        print(f"❌ Analysis error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "type": "error",
            "content_en": f"Analysis failed: {str(e)[:100]}"
        })

    finally:
        if audio_path and os.path.exists(audio_path):
            try:
                os.remove(audio_path)
            except:
                pass