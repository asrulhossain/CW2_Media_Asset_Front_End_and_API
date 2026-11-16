from flask import Blueprint, make_response, jsonify, request
from bson import ObjectId
import datetime
from decorators import jwt_required, get_token_data
import globals

projects_bp = Blueprint('projects_bp', __name__)
projects = globals.db.projects
assets = globals.db.assets

statuses = ["In Progress", "Review", "Completed"]

@projects_bp.route("/api/v1.0/projects", methods=["GET"])
@jwt_required
def show_all_projects():
    data = get_token_data()
    page_num, page_size = 1, 10
    try:
        if request.args.get('pn'): page_num = int(request.args.get('pn'))
        if request.args.get('ps'): page_size = int(request.args.get('ps'))
    except ValueError:
        return make_response(jsonify({"error": "pn and ps must be numbers"}), 400)
    if page_num < 1 or page_size < 1: return make_response(jsonify({"error": "pn and ps must be 1 or more"}), 400)
    page_start = (page_size * (page_num - 1))

    # Creators only see their own projects, admins see all
    query = {}
    if data["role"] != "Admin": query["user_id"] = ObjectId(data["user_id"])

    data_to_return = []
    for project in projects.find(query).skip(page_start).limit(page_size):
        project['_id'] = str(project['_id'])
        project['user_id'] = str(project['user_id'])
        data_to_return.append(project)
    return make_response(jsonify(data_to_return), 200)

@projects_bp.route("/api/v1.0/projects/<string:project_id>", methods=["GET"])
@jwt_required
def show_one_project(project_id):
    if not ObjectId.is_valid(project_id): return make_response(jsonify({"error": "Invalid ID format"}), 400)
    data = get_token_data()
    project = projects.find_one({'_id': ObjectId(project_id)})
    if project:
        if data["role"] != "Admin" and str(project["user_id"]) != data["user_id"]: return make_response(jsonify({"error": "Access denied"}), 403)
        project['_id'] = str(project['_id'])
        project['user_id'] = str(project['user_id'])

        # Totals for this project's assets
        project['asset_count'], project['total_size_gb'] = 0, 0
        for total in assets.aggregate([{"$match": {"project_id": ObjectId(project_id)}}, {"$group": {"_id": None, "count": {"$sum": 1}, "size": {"$sum": "$file_size_gb"}}}]):
            project['asset_count'], project['total_size_gb'] = total['count'], round(total['size'], 2)
        return make_response(jsonify(project), 200)
    return make_response(jsonify({"error": "Project not found"}), 404)

@projects_bp.route("/api/v1.0/projects", methods=["POST"])
@jwt_required
def add_project():
    data = get_token_data()
    if "title" in request.form:
        if request.form.get("status", "In Progress") not in statuses: return make_response(jsonify({"error": "status must be In Progress, Review or Completed"}), 400)
        new_project = {
            "user_id": ObjectId(data["user_id"]), "title": request.form["title"],
            "target_region": request.form.get("target_region", "Global"), "status": request.form.get("status", "In Progress"),
            "created_date": datetime.datetime.now().strftime("%Y-%m-%d")
        }
        new_project_id = projects.insert_one(new_project)
        return make_response(jsonify({"url": "http://127.0.0.1:5001/api/v1.0/projects/" + str(new_project_id.inserted_id)}), 201)
    return make_response(jsonify({"error": "Missing form data"}), 400)

@projects_bp.route("/api/v1.0/projects/<string:project_id>", methods=["PUT"])
@jwt_required
def edit_project(project_id):
    if not ObjectId.is_valid(project_id): return make_response(jsonify({"error": "Invalid ID format"}), 400)
    data = get_token_data()
    project = projects.find_one({"_id": ObjectId(project_id)})
    if project is None: return make_response(jsonify({"error": "Project not found"}), 404)
    if data["role"] != "Admin" and str(project["user_id"]) != data["user_id"]: return make_response(jsonify({"error": "Access denied"}), 403)

    if "title" in request.form and "status" in request.form:
        if request.form["status"] not in statuses: return make_response(jsonify({"error": "status must be In Progress, Review or Completed"}), 400)
        projects.update_one({"_id": ObjectId(project_id)}, {"$set": {"title": request.form["title"], "status": request.form["status"], "target_region": request.form.get("target_region", project["target_region"])}})
        return make_response(jsonify({"url": "http://127.0.0.1:5001/api/v1.0/projects/" + project_id}), 200)
    return make_response(jsonify({"error": "Missing form data"}), 400)

@projects_bp.route("/api/v1.0/projects/<string:project_id>", methods=['DELETE'])
@jwt_required
def delete_project(project_id):
    if not ObjectId.is_valid(project_id): return make_response(jsonify({"error": "Invalid ID format"}), 400)
    data = get_token_data()
    project = projects.find_one({"_id": ObjectId(project_id)})
    if project is None: return make_response(jsonify({"error": "Project not found"}), 404)
    if data["role"] != "Admin" and str(project["user_id"]) != data["user_id"]: return make_response(jsonify({"error": "Access denied"}), 403)

    # Delete the project's assets
    assets.delete_many({"project_id": ObjectId(project_id)})
    projects.delete_one({"_id": ObjectId(project_id)})
    return make_response(jsonify({"message": "Project deleted!"}), 200)
