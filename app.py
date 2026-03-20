from flask import Flask
from flask_cors import CORS

from routes.upload_routes import upload_bp
from routes.analysis_routes import analysis_bp
from routes.auth_routes import auth_bp
from routes.link_routes import link_bp
from routes.video_routes import video_bp
from flask import send_from_directory
from routes.post_routes import post_bp

app = Flask(__name__)

# allow frontend from any device
CORS(app)

# register routes
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

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",   # IMPORTANT
        port=5000,
        debug=True
    )
