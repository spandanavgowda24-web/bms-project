from flask import Blueprint, request, jsonify
from database.db import interactions_collection, responses_collection

# Create Blueprint
speech_bp = Blueprint("speech_bp", __name__)


# ==============================
# Speech Input API
# ==============================
@speech_bp.route("/speech-input", methods=["POST"])
def speech_input():

    data = request.json

    user_id = data.get("user_id")
    session_id = data.get("session_id")
    speech_text = data.get("speech_text")

    if not speech_text:
        return jsonify({
            "error": "Speech text is required"
        }), 400

    # Store interaction in MongoDB
    interaction_data = {
        "user_id": user_id,
        "session_id": session_id,
        "speech_text": speech_text
    }

    result = interactions_collection.insert_one(interaction_data)

    interaction_data["_id"] = str(result.inserted_id)

    return jsonify({
        "message": "Speech interaction stored successfully",
        "data": interaction_data
    })


# ==============================
# Get Session History API
# ==============================
@speech_bp.route("/get-session-history/<session_id>", methods=["GET"])
def get_session_history(session_id):

    interactions = interactions_collection.find({
        "session_id": session_id
    })

    history = []

    for interaction in interactions:
        interaction["_id"] = str(interaction["_id"])
        history.append(interaction)

    return jsonify({
        "session_id": session_id,
        "history": history
    })


# ==============================
# Generate Response API
# ==============================
@speech_bp.route("/generate-response", methods=["POST"])
def generate_response():

    data = request.json

    user_id = data.get("user_id")
    session_id = data.get("session_id")
    speech_text = data.get("speech_text")

    if not speech_text:
        return jsonify({
            "error": "Speech text is required"
        }), 400

    # Dummy intelligent response
    response_text = f"System received: {speech_text}"

    response_data = {
        "user_id": user_id,
        "session_id": session_id,
        "speech_text": speech_text,
        "response_text": response_text
    }

    # Store response in MongoDB
    result = responses_collection.insert_one(response_data)

    response_data["_id"] = str(result.inserted_id)

    return jsonify({
        "message": "Response generated and stored successfully",
        "data": response_data
    })
# ==============================
# Conversation Timeline API
# ==============================
@speech_bp.route("/conversation-timeline/<session_id>", methods=["GET"])
def conversation_timeline(session_id):

    interactions = list(interactions_collection.find({
        "session_id": session_id
    }))

    responses = list(responses_collection.find({
        "session_id": session_id
    }))

    # Convert ObjectIds
    for i in interactions:
        i["_id"] = str(i["_id"])

    for r in responses:
        r["_id"] = str(r["_id"])

    return jsonify({
        "session_id": session_id,
        "interactions": interactions,
        "responses": responses
    })

