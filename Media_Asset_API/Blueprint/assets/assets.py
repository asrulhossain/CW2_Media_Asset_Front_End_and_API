from flask import Blueprint, make_response, jsonify, request
from bson import ObjectId
import datetime
import re
from decorators import jwt_required, get_token_data
import globals

assets_bp = Blueprint('assets_bp', __name__)
assets = globals.db.assets
projects = globals.db.projects

formats = [".mp4", ".mov", ".mxf", ".braw", ".r3d", ".wav"]

@assets_bp.route("/api/v1.0/projects/<string:project_id>/assets", methods=["GET"])
@jwt_required
def show_project_assets(project_id):
    if not ObjectId.is_valid(project_id): return make_response(jsonify({"error": "Invalid ID format"}), 400)
    data = get_token_data()
    project = projects.find_one({"_id": ObjectId(project_id)})
    if project is None: return make_response(jsonify({"error": "Project not found"}), 404)
    if data["role"] != "Admin" and str(project["user_id"]) != data["user_id"]: return make_response(jsonify({"error": "Access denied"}), 403)

    page_num, page_size = 1, 10
    try:
        if request.args.get('pn'): page_num = int(request.args.get('pn'))
        if request.args.get('ps'): page_size = int(request.args.get('ps'))
    except ValueError:
        return make_response(jsonify({"error": "pn and ps must be numbers"}), 400)
    if page_num < 1 or page_size < 1: return make_response(jsonify({"error": "pn and ps must be 1 or more"}), 400)
    page_start = (page_size * (page_num - 1))

    # Optional filters
    query = {"project_id": ObjectId(project_id)}
    if request.args.get('format'): query["file_format"] = request.args.get('format')
    if request.args.get('drive'): query["drive_location"] = request.args.get('drive')
    if request.args.get('tag'): query["tags.tag_name"] = request.args.get('tag')
    if request.args.get('has_proxy'): query["has_proxy"] = request.args.get('has_proxy').lower() == "true"

    data_to_return = []
    for asset in assets.find(query).skip(page_start).limit(page_size):
        asset['_id'] = str(asset['_id'])
        asset['user_id'] = str(asset['user_id'])
        asset['project_id'] = str(asset['project_id'])
        for tag in asset.get('tags', []): tag['tag_id'] = str(tag['tag_id'])
        for log in asset.get('audit_logs', []):
            log['_id'] = str(log['_id'])
            for task in log.get('tasks', []): task['_id'] = str(task['_id'])
        data_to_return.append(asset)
    return make_response(jsonify(data_to_return), 200)

@assets_bp.route("/api/v1.0/search", methods=["GET"])
@jwt_required
def search_assets():
    data = get_token_data()
    query = request.args.get('query', '')
    if not query:
        return make_response(jsonify({"error": "Please provide a query parameter '?query=search_term'"}), 400)

    # Go through the asset, its tags and its project, and show which drive it is on
    text = {"$regex": re.escape(query), "$options": "i"}
    owner = {}
    if data["role"] != "Admin": owner["user_id"] = ObjectId(data["user_id"])
    pipeline = [
        {"$match": owner},
        {"$lookup": {"from": "projects", "localField": "project_id", "foreignField": "_id", "as": "project"}},
        {"$unwind": "$project"},
        {"$match": {"$or": [{"filename": text}, {"drive_location": text}, {"tags.tag_name": text}, {"project.title": text}]}}
    ]

    search_results = []
    for asset in assets.aggregate(pipeline):
        search_results.append({
            "_id": str(asset["_id"]), "filename": asset["filename"], "drive_location": asset["drive_location"],
            "project_title": asset["project"]["title"], "tags": [tag["tag_name"] for tag in asset.get("tags", [])]
        })
    return make_response(jsonify({"results": search_results, "count": len(search_results)}), 200)

@assets_bp.route("/api/v1.0/assets/<string:asset_id>", methods=["GET"])
@jwt_required
def show_one_asset(asset_id):
    if not ObjectId.is_valid(asset_id): return make_response(jsonify({"error": "Invalid ID format"}), 400)
    data = get_token_data()
    asset = assets.find_one({'_id': ObjectId(asset_id)})
    if asset:
        if data["role"] != "Admin" and str(asset["user_id"]) != data["user_id"]: return make_response(jsonify({"error": "Access denied"}), 403)
        asset['_id'] = str(asset['_id'])
        asset['user_id'] = str(asset['user_id'])
        asset['project_id'] = str(asset['project_id'])
        for tag in asset.get('tags', []): tag['tag_id'] = str(tag['tag_id'])
        for log in asset.get('audit_logs', []):
            log['_id'] = str(log['_id'])
            for task in log.get('tasks', []): task['_id'] = str(task['_id'])
        return make_response(jsonify(asset), 200)
    return make_response(jsonify({"error": "Asset not found"}), 404)

@assets_bp.route("/api/v1.0/projects/<string:project_id>/assets", methods=["POST"])
@jwt_required
def add_asset(project_id):
    if not ObjectId.is_valid(project_id): return make_response(jsonify({"error": "Invalid ID format"}), 400)
    data = get_token_data()
    project = projects.find_one({"_id": ObjectId(project_id)})
    if project is None: return make_response(jsonify({"error": "Project not found"}), 404)
    if data["role"] != "Admin" and str(project["user_id"]) != data["user_id"]: return make_response(jsonify({"error": "Access denied"}), 403)

    if "filename" in request.form and "file_format" in request.form and "drive_location" in request.form:
        if request.form["file_format"] not in formats: return make_response(jsonify({"error": "file_format must be one of: " + ", ".join(formats)}), 400)
        try:
            file_size_gb = float(request.form.get("file_size_gb", 0.0))
            if not (0 <= file_size_gb <= 100000): raise ValueError
        except ValueError:
            return make_response(jsonify({"error": "file_size_gb must be a positive number"}), 400)

        new_asset = {
            "project_id": ObjectId(project_id), "user_id": project["user_id"],
            "filename": request.form["filename"], "file_format": request.form["file_format"],
            "file_size_gb": file_size_gb, "resolution": request.form.get("resolution", "1920x1080"),
            "drive_location": request.form["drive_location"], "has_proxy": request.form.get("has_proxy", "false").lower() == "true",
            "created_timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "tags": [], "audit_logs": []
        }
        new_asset_id = assets.insert_one(new_asset)
        return make_response(jsonify({"url": "http://127.0.0.1:5001/api/v1.0/assets/" + str(new_asset_id.inserted_id)}), 201)
    return make_response(jsonify({"error": "Missing form data"}), 400)

@assets_bp.route("/api/v1.0/assets/<string:asset_id>", methods=["PUT"])
@jwt_required
def edit_asset(asset_id):
    if not ObjectId.is_valid(asset_id): return make_response(jsonify({"error": "Invalid ID format"}), 400)
    data = get_token_data()
    asset = assets.find_one({"_id": ObjectId(asset_id)})
    if asset is None: return make_response(jsonify({"error": "Asset not found"}), 404)
    if data["role"] != "Admin" and str(asset["user_id"]) != data["user_id"]: return make_response(jsonify({"error": "Access denied"}), 403)

    if "filename" in request.form and "file_format" in request.form:
        if request.form["file_format"] not in formats: return make_response(jsonify({"error": "file_format must be one of: " + ", ".join(formats)}), 400)
        # Keep the old value for anything that was not sent
        assets.update_one({"_id": ObjectId(asset_id)}, {"$set": {
            "filename": request.form["filename"], "file_format": request.form["file_format"],
            "drive_location": request.form.get("drive_location", asset["drive_location"]),
            "has_proxy": request.form.get("has_proxy", str(asset["has_proxy"])).lower() == "true"}})
        return make_response(jsonify({"url": "http://127.0.0.1:5001/api/v1.0/assets/" + asset_id}), 200)
    return make_response(jsonify({"error": "Missing form data"}), 400)

@assets_bp.route("/api/v1.0/assets/<string:asset_id>", methods=['DELETE'])
@jwt_required
def delete_asset(asset_id):
    if not ObjectId.is_valid(asset_id): return make_response(jsonify({"error": "Invalid ID format"}), 400)
    data = get_token_data()
    asset = assets.find_one({"_id": ObjectId(asset_id)})
    if asset is None: return make_response(jsonify({"error": "Asset not found"}), 404)
    if data["role"] != "Admin" and str(asset["user_id"]) != data["user_id"]: return make_response(jsonify({"error": "Access denied"}), 403)

    assets.delete_one({"_id": ObjectId(asset_id)})
    return make_response(jsonify({"message": "Asset deleted!!!"}), 200)
