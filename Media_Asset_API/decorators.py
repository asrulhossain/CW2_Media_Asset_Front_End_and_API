from functools import wraps
import globals
import jwt
from flask import jsonify, make_response, request

blacklist = globals.db.blacklist


def get_token_data():
  # Returns the details stored in the logged-in user's token 
  token = request.headers.get("x-access-token")
  return jwt.decode(token, globals.secret_key, algorithms=["HS256"])


def admin_required(func):

  @wraps(func)
  def admin_required_wrapper(*args, **kwargs):
    token = request.headers.get("x-access-token")
    if not token:
      return make_response(jsonify({"message": "Token is missing..."}), 401)
    try:
      data = jwt.decode(token, globals.secret_key, algorithms=["HS256"])
    except Exception:
      return make_response(jsonify({"message": "Token is invalid"}), 401)

    # Check if token is blacklisted
    bl_token = blacklist.find_one({"token": token})
    if bl_token is not None:
      return make_response(
          jsonify({"message": "Token has been cancelled.."}), 401
      )

    # Check admin role
    if data.get("role") == "Admin":
      return func(*args, **kwargs)
    else:
      return make_response(
          jsonify({"message": "Admin access required"}), 403
      )

  return admin_required_wrapper


def jwt_required(func):

  @wraps(func)
  def jwt_required_wrapper(*args, **kwargs):
    token = request.headers.get("x-access-token")
    if not token:
      return make_response(jsonify({"message": "Token is missing..."}), 401)
    try:
      data = jwt.decode(token, globals.secret_key, algorithms=["HS256"])
    except Exception:
      return make_response(jsonify({"message": "Token is invalid"}), 401)

    bl_token = blacklist.find_one({"token": token})
    if bl_token is not None:
      return make_response(
          jsonify({"message": "Token has been cancelled.."}), 401
      )

    return func(*args, **kwargs)

  return jwt_required_wrapper
