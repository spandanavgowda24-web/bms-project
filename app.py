# app.py - UPDATED with translation endpoint
from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS

from routes.upload_routes import upload_bp
from routes.analysis_routes import analysis_bp
from routes.auth_routes import auth_bp
from routes.link_routes import link_bp
from routes.video_routes import video_bp
from routes.post_routes import post_bp

from services.tts_service import generate_speech

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

app.register_blueprint(upload_bp)
app.register_blueprint(analysis_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(link_bp)
app.register_blueprint(video_bp)
app.register_blueprint(post_bp)


@app.route("/")
def home():
    return "AI Voice Guide Backend Running"


@app.route("/uploads/<filename>")
def serve_video(filename):
    return send_from_directory("uploads", filename)


@app.route("/tts/<filename>")
def serve_audio(filename):
    return send_from_directory("tts_audio", filename)


@app.route("/generate-audio", methods=["POST"])
def generate_audio_api():
    try:
        data = request.get_json()

        text = data.get("text", "")
        lang = data.get("lang", "en")
        voice = data.get("voice", "female")
        speed = data.get("speed", "normal")

        if not text:
            return jsonify({"error": "No text"}), 400

        file = generate_speech(text, lang, voice, speed)

        if not file:
            return jsonify({"error": "TTS failed"}), 500

        return jsonify({"audio": file})

    except Exception as e:
        print("API ERROR:", e)
        return jsonify({"error": "Server error"}), 500


# Translation test endpoint
@app.route("/test-translate", methods=["POST"])
def test_translate():
    try:
        from services.translator import translate_list

        data = request.json
        text = data.get("text", "Hello, welcome to the AI Voice Guide")
        target = data.get("target", "hi")

        result = translate_list([text], target)

        return jsonify({
            "original": text,
            "translated": result[0] if result else text,
            "target": target,
            "success": True
        })
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


if __name__ == "__main__":
    print("\n🚀 Starting AI Voice Guide Backend...")
    print("📢 Translation support: English, Hindi, Kannada")
    app.run(host="0.0.0.0", port=5000, debug=True)