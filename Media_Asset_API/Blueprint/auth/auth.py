import datetime
import jwt
from flask import Blueprint, jsonify, make_response, request
from werkzeug.security import generate_password_hash, check_password_hash
from decorators import jwt_required
import globals

users = globals.db.users
blacklist = globals.db.blacklist

auth_bp = Blueprint("auth_bp", __name__)


@auth_bp.route("/api/v1.0/register", methods=["POST"])
def register():
    if "name" in request.form and "email" in request.form and "password" in request.form:
        if len(request.form["password"]) < 8:
            return make_response(jsonify({"error": "Password must be at least 8 characters"}), 400)
        if users.find_one({"email": request.form["email"].lower()}):
            return make_response(jsonify({"error": "Email already exists"}), 409)

        new_user = {
            "name": request.form["name"],
            "email": request.form["email"].lower(),
            "password_hash": generate_password_hash(request.form["password"]),
            "role": "Creator",
            "profile": {"department": "Unassigned", "joined_date": datetime.datetime.now().strftime("%Y-%m-%d"), "is_active": True},
            "storage_metrics": {"max_quota_gb": 500.0, "used_quota_gb": 0.0, "quota_warning": False},
            "media_permissions": {"assigned_drives": ["NAS_Archive"], "allowed_formats": [".mp4", ".mov"], "max_allowed_resolution": "1920x1080", "can_generate_proxy": False},
            "recent_activity": []
        }
        new_id = users.insert_one(new_user)
        return make_response(jsonify({
            "message": "User registered successfully",
            "id": str(new_id.inserted_id)
        }), 201)

    return make_response(jsonify({"error": "Missing registration details"}), 400)


@auth_bp.route("/api/v1.0/login", methods=["POST"])
def login():
    auth = request.authorization
    if auth:
        user = users.find_one({"email": auth.username.lower()})
        if user is not None:
            if check_password_hash(user["password_hash"], auth.password):
                token = jwt.encode(
                    {
                        "user": user["email"],
                        "user_id": str(user["_id"]),
                        "role": user.get("role", "Creator"),
                        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30),
                    },
                    globals.secret_key,
                    algorithm="HS256",
                )
                return make_response(jsonify({"token": token}), 200)
            else:
                return make_response(jsonify({"message": "Bad password"}), 401)
        else:
            return make_response(jsonify({"message": "Bad username"}), 401)

    return make_response(
        "Could not verify",
        401,
        {"WWW-Authenticate": 'Basic realm="Login required"'},
    )


@auth_bp.route("/api/v1.0/logout", methods=["GET"])
@jwt_required
def logout():
    token = request.headers.get("x-access-token")
    blacklist.insert_one({"token": token})
    return make_response(jsonify({"message": "Logout successful"}), 200)
