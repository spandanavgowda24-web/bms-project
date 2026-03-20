from flask import Blueprint, request, jsonify
import bcrypt
import jwt
from datetime import datetime, timedelta

from database import users_collection
from config import JWT_SECRET, JWT_ALGORITHM

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


# REGISTER
@auth_bp.route("/register", methods=["POST"])
def register():

    data = request.json

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"message": "Missing fields"}), 400

    existing = users_collection.find_one({"username": username})

    if existing:
        return jsonify({"message": "User already exists"}), 400

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    user = {
        "username": username,
        "email": email,
        "password": hashed
    }

    result = users_collection.insert_one(user)

    return jsonify({
        "message": "User registered successfully",
        "user_id": str(result.inserted_id)
    }), 200


# LOGIN
@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.json

    username = data.get("username")
    password = data.get("password")

    user = users_collection.find_one({"username": username})

    if not user:
        return jsonify({"message": "User not found"}), 404

    stored_password = user["password"]

    if isinstance(stored_password, str):
        stored_password = stored_password.encode()

    if not bcrypt.checkpw(password.encode(), stored_password):
        return jsonify({"message": "Incorrect password"}), 401

    token = jwt.encode(
        {
            "user_id": str(user["_id"]),
            "exp": datetime.utcnow() + timedelta(days=1)
        },
        JWT_SECRET,
        algorithm=JWT_ALGORITHM
    )

    return jsonify({
        "message": "Login successful",
        "token": token,
        "user_id": str(user["_id"]),
        "username": user["username"]
    })