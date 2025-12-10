from flask import Blueprint, request, jsonify

from app.courts import bp
from app.dal.repository import get_court_by_id
from app.dal.repository import update_court_owner


@bp.route("/<court_id>", methods=["GET"])
def get_court(court_id):
    court = get_court_by_id(court_id)
    if court:
        return jsonify(court)
    else:
        return jsonify({"message": "Court not found"}), 404
    
@bp.route("/update_owner", methods=["POST"])
def update_owner():
    data = request.json
    court_id = data.get("court_id")
    new_owner_id = data.get("new_owner_id")
    if not court_id or not new_owner_id:
        return jsonify({"status": "error", "message": "缺少参数"}), 400
    try:
        update_court_owner(court_id, new_owner_id)
        return jsonify({"status": "success", "message": "场地拥有者已更新"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
@bp.route("/swap_owner", methods=["POST"])
def swap_owner():
    data = request.json
    court_id_1 = data.get("court_id_1")
    new_owner_1 = data.get("new_owner_1")
    court_id_2 = data.get("court_id_2")
    new_owner_2 = data.get("new_owner_2")
    if not all([court_id_1, new_owner_1, court_id_2, new_owner_2]):
        return jsonify({"status": "error", "message": "缺少参数"}), 400
    try:
        update_court_owner(court_id_1, new_owner_1)
        update_court_owner(court_id_2, new_owner_2)
        return jsonify({"status": "success", "message": "场地交换成功"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500