from flask import Flask
from flask_cors import CORS
from app.routes.speech_routes import speech_bp


def create_app():
    app = Flask(__name__)

    CORS(app)

    @app.route("/")
    def home():
        return {
            "message": "Intelligent Speech Interaction Backend Running"
        }

    app.register_blueprint(speech_bp)

    return app
