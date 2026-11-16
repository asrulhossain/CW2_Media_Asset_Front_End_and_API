from flask import Blueprint, make_response, jsonify, request
from bson import ObjectId
from decorators import jwt_required, get_token_data
import globals

tags_bp = Blueprint('tags_bp', __name__)
tags = globals.db.tags
assets = globals.db.assets

@tags_bp.route("/api/v1.0/tags", methods=["GET"])
@jwt_required
def show_all_tags():
    data_to_return = []
    for tag in tags.find():
        tag['_id'] = str(tag['_id'])
        data_to_return.append(tag)
    return make_response(jsonify(data_to_return), 200)

@tags_bp.route("/api/v1.0/tags", methods=["POST"])
@jwt_required
def add_global_tag():
    if "tag_name" in request.form:
        if tags.find_one({"tag_name": request.form["tag_name"]}):
            return make_response(jsonify({"error": "Tag already exists"}), 409)
        new_tag_id = tags.insert_one({"tag_name": request.form["tag_name"], "category": request.form.get("category", "Content")})
        return make_response(jsonify({"message": "Tag created", "tag_id": str(new_tag_id.inserted_id)}), 201)
    return make_response(jsonify({"error": "Missing form data"}), 400)

@tags_bp.route("/api/v1.0/assets/<string:asset_id>/tags", methods=['POST'])
@jwt_required
def add_tag(asset_id):
    if not ObjectId.is_valid(asset_id): return make_response(jsonify({"error": "Invalid asset ID format"}), 400)
    data = get_token_data()
    asset = assets.find_one({"_id": ObjectId(asset_id)})
    if asset is None: return make_response(jsonify({"error": "Asset not found"}), 404)
    if data["role"] != "Admin" and str(asset["user_id"]) != data["user_id"]: return make_response(jsonify({"error": "Access denied"}), 403)

    if "tag_name" in request.form:
        # The tag must already exist in the global tags list
        tag = tags.find_one({"tag_name": request.form["tag_name"]})
        if tag is None: return make_response(jsonify({"error": "Tag not found, create it first"}), 404)
        for existing in asset["tags"]:
            if existing["tag_id"] == tag["_id"]: return make_response(jsonify({"error": "Tag already on this asset"}), 409)

        assets.update_one({"_id": ObjectId(asset_id)}, {"$push": {"tags": {"tag_id": tag["_id"], "tag_name": tag["tag_name"]}}})
        return make_response(jsonify({"message": f"Tag '{tag['tag_name']}' added to asset", "tag_id": str(tag["_id"])}), 201)
    else:
        return make_response(jsonify({"error": "Missing 'tag_name' in form data"}), 400)

@tags_bp.route("/api/v1.0/assets/<string:asset_id>/tags/<string:tag_id>", methods=['DELETE'])
@jwt_required
def remove_tag(asset_id, tag_id):
    if not ObjectId.is_valid(asset_id) or not ObjectId.is_valid(tag_id): return make_response(jsonify({"error": "Invalid ID format"}), 400)
    data = get_token_data()
    asset = assets.find_one({"_id": ObjectId(asset_id)})
    if asset is None: return make_response(jsonify({"error": "Asset not found"}), 404)
    if data["role"] != "Admin" and str(asset["user_id"]) != data["user_id"]: return make_response(jsonify({"error": "Access denied"}), 403)

    result = assets.update_one({"_id": ObjectId(asset_id)}, {"$pull": {"tags": {"tag_id": ObjectId(tag_id)}}})
    if result.modified_count == 1: return make_response(jsonify({"message": "Tag removed from asset"}), 200)
    return make_response(jsonify({"error": "Tag is not on this asset"}), 404)
