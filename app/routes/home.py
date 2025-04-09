from flask import Blueprint, jsonify

home_bp = Blueprint("main", __name__)

@home_bp.route("/", methods=["GET"])
def home():
    return jsonify({"message": "---API SOCIALITEC---"}),200
