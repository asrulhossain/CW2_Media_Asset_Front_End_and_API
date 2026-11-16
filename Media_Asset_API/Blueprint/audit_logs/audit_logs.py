from flask import Blueprint, make_response, jsonify, request
from bson import ObjectId
from decorators import jwt_required, get_token_data
import globals

audit_logs_bp = Blueprint("audit_logs_bp", __name__)
assets = globals.db.assets

actions = ["UPLOADED", "MODIFIED", "REVIEWED", "ARCHIVED", "EXPORTED"]

@audit_logs_bp.route("/api/v1.0/assets/<string:asset_id>/audit_logs", methods=['POST'])
@jwt_required
def add_new_audit_log(asset_id):
    if not ObjectId.is_valid(asset_id): return make_response(jsonify({"error": "Invalid asset ID format"}), 400)
    data = get_token_data()
    asset = assets.find_one({"_id": ObjectId(asset_id)})
    if asset is None: return make_response(jsonify({"error": "Asset not found"}), 404)
    if data["role"] != "Admin" and str(asset["user_id"]) != data["user_id"]: return make_response(jsonify({"error": "Access denied"}), 403)

    if "action" in request.form:
        if request.form["action"] not in actions: return make_response(jsonify({"error": "action must be one of: " + ", ".join(actions)}), 400)
        new_log = {
            "_id": ObjectId(),
            "action": request.form['action'],
            "tasks": []
        }

        assets.update_one(
            {"_id": ObjectId(asset_id)},
            {"$push": {"audit_logs": new_log}}
        )
        new_log_link = "http://127.0.0.1:5001/api/v1.0/assets/" + asset_id + "/audit_logs/" + str(new_log["_id"])
        return make_response(jsonify({"url": new_log_link}), 201)
    else:
        return make_response(jsonify({"error": "Missing form data"}), 400)

@audit_logs_bp.route("/api/v1.0/assets/<string:asset_id>/audit_logs/<string:log_id>", methods=['PUT'])
@jwt_required
def update_audit_log(asset_id, log_id):
    if not ObjectId.is_valid(asset_id) or not ObjectId.is_valid(log_id): return make_response(jsonify({"error": "Invalid ID format"}), 400)
    data = get_token_data()
    asset = assets.find_one({"_id": ObjectId(asset_id)})
    if asset is None: return make_response(jsonify({"error": "Asset not found"}), 404)
    if data["role"] != "Admin" and str(asset["user_id"]) != data["user_id"]: return make_response(jsonify({"error": "Access denied"}), 403)

    if "action" in request.form:
        if request.form["action"] not in actions: return make_response(jsonify({"error": "action must be one of: " + ", ".join(actions)}), 400)
        results = assets.update_one(
            {"_id": ObjectId(asset_id), "audit_logs._id": ObjectId(log_id)},
            {"$set": {"audit_logs.$.action": request.form["action"]}}
        )

        if results.matched_count == 1: return make_response(jsonify({"message": "Audit log updated"}), 200)
        else: return make_response(jsonify({"error": "Log not found"}), 404)
    else: return make_response(jsonify({"error": "Missing form data"}), 400)

@audit_logs_bp.route("/api/v1.0/assets/<string:asset_id>/audit_logs/<string:log_id>", methods=['DELETE'])
@jwt_required
def delete_audit_log(asset_id, log_id):
    if not ObjectId.is_valid(asset_id) or not ObjectId.is_valid(log_id): return make_response(jsonify({"error": "Invalid ID format"}), 400)
    data = get_token_data()
    asset = assets.find_one({"_id": ObjectId(asset_id)})
    if asset is None: return make_response(jsonify({"error": "Asset not found"}), 404)
    if data["role"] != "Admin" and str(asset["user_id"]) != data["user_id"]: return make_response(jsonify({"error": "Access denied"}), 403)

    result = assets.update_one(
        {"_id": ObjectId(asset_id)},
        {"$pull": {"audit_logs": {"_id": ObjectId(log_id)}}}
    )

    if result.modified_count == 1: return make_response(jsonify({"message": "Audit log deleted successfully!!!"}), 200)
    else: return make_response(jsonify({"error": "Log not found"}), 404)
