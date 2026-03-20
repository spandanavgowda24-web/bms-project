from flask import Blueprint, request, jsonify
import jwt
from config import JWT_SECRET, JWT_ALGORITHM
from database import analysis_collection

history_bp = Blueprint("history", __name__)


def verify_token(token):
    try:
        data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return data["user_id"]
    except:
        return None


@history_bp.route("/history", methods=["GET"])
def get_history():

    token = request.headers.get("Authorization")

    if not token:
        return jsonify({"message": "Token missing"}), 401

    token = token.split(" ")[1]
    user_id = verify_token(token)

    if not user_id:
        return jsonify({"message": "Invalid token"}), 401

    history = list(analysis_collection.find(
        {"user_id": user_id},
        {"_id": 0}
    ))

    return jsonify(history)