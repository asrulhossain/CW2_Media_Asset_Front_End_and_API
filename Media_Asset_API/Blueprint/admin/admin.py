from flask import Blueprint, make_response, jsonify, request
from bson import ObjectId
from decorators import jwt_required, admin_required, get_token_data
import globals

admin_bp = Blueprint('admin_bp', __name__)
users = globals.db.users
projects = globals.db.projects
assets = globals.db.assets
tags = globals.db.tags

@admin_bp.route("/api/v1.0/admin/users", methods=["GET"])
@jwt_required
@admin_required
def show_all_users():
    page_num, page_size = 1, 10
    try:
        if request.args.get('pn'): page_num = int(request.args.get('pn'))
        if request.args.get('ps'): page_size = int(request.args.get('ps'))
    except ValueError:
        return make_response(jsonify({"error": "pn and ps must be numbers"}), 400)
    if page_num < 1 or page_size < 1: return make_response(jsonify({"error": "pn and ps must be 1 or more"}), 400)
    page_start = (page_size * (page_num - 1))

    data_to_return = []
    for user in users.find({}, {"password_hash": 0}).skip(page_start).limit(page_size):
        user['_id'] = str(user['_id'])
        data_to_return.append(user)
    return make_response(jsonify(data_to_return), 200)

@admin_bp.route("/api/v1.0/admin/projects", methods=["GET"])
@jwt_required
@admin_required
def show_all_projects():
    page_num, page_size = 1, 10
    try:
        if request.args.get('pn'): page_num = int(request.args.get('pn'))
        if request.args.get('ps'): page_size = int(request.args.get('ps'))
    except ValueError:
        return make_response(jsonify({"error": "pn and ps must be numbers"}), 400)
    if page_num < 1 or page_size < 1: return make_response(jsonify({"error": "pn and ps must be 1 or more"}), 400)
    page_start = (page_size * (page_num - 1))

    # $lookup adds the owner's name and email to each project
    pipeline = [
        {"$lookup": {"from": "users", "localField": "user_id", "foreignField": "_id", "as": "owner"}},
        {"$unwind": "$owner"},
        {"$skip": page_start},
        {"$limit": page_size}
    ]
    data_to_return = []
    for project in projects.aggregate(pipeline):
        project['_id'] = str(project['_id'])
        project['user_id'] = str(project['user_id'])
        project['owner'] = {"name": project['owner']['name'], "email": project['owner']['email']}
        data_to_return.append(project)
    return make_response(jsonify(data_to_return), 200)

@admin_bp.route("/api/v1.0/admin/users/<string:user_id>", methods=['DELETE'])
@jwt_required
@admin_required
def delete_user(user_id):
    if not ObjectId.is_valid(user_id): return make_response(jsonify({"error": "Invalid ID format"}), 400)
    data = get_token_data()
    if user_id == data["user_id"]: return make_response(jsonify({"error": "You cannot delete your own account"}), 400)

    result = users.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 1:
        # Delete the user's assets and projects 
        assets.delete_many({"user_id": ObjectId(user_id)})
        projects.delete_many({"user_id": ObjectId(user_id)})
        return make_response(jsonify({"message": "User deleted!"}), 200)
    return make_response(jsonify({"error": "User not found"}), 404)

@admin_bp.route("/api/v1.0/admin/tags", methods=["POST"])
@jwt_required
@admin_required
def add_global_tag():
    if "tag_name" in request.form:
        if tags.find_one({"tag_name": request.form["tag_name"]}):
            return make_response(jsonify({"error": "Tag already exists"}), 409)
        new_tag_id = tags.insert_one({"tag_name": request.form["tag_name"], "category": request.form.get("category", "Content")})
        return make_response(jsonify({"message": "Tag created", "tag_id": str(new_tag_id.inserted_id)}), 201)
    return make_response(jsonify({"error": "Missing form data"}), 400)
