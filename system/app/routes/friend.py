from flask import Blueprint, request, jsonify
from app import mysql
from datetime import datetime

bp = Blueprint('friend', __name__, url_prefix='/friend')

# 添加好友接口
@bp.route('/add', methods=['POST'])
def add_friend():
    data = request.json
    my_id = data.get('my_id')
    search_id = data.get('search_id')

    if not my_id or not search_id:
        return jsonify({"status": "error", "message": "缺少必要的参数"}), 400

    try:
        with mysql.connection.cursor() as cursor:
            # 检查是否已经是好友
            sql_check_friend = """
                SELECT COUNT(*) FROM Friend
                WHERE (Friend_a_id = %s AND Friend_b_id = %s) OR (Friend_a_id = %s AND Friend_b_id = %s)
            """
            cursor.execute(sql_check_friend, (my_id, search_id, search_id, my_id))
            if cursor.fetchone()[0] > 0:
                return jsonify({"status": "error", "message": "已经是好友"}), 400

            # 添加好友
            sql_add_friend = """
                INSERT INTO Friend (Friend_a_id, Friend_b_id) VALUES (%s, %s)
            """
            cursor.execute(sql_add_friend, (my_id, search_id))
            mysql.connection.commit()

    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

    return jsonify({"status": "success", "message": "好友添加成功"}), 201

# 删除好友接口
@bp.route('/delete', methods=['POST'])
def delete_friend():
    data = request.json
    my_id = data.get('my_id')
    search_id = data.get('search_id')

    if not my_id or not search_id:
        return jsonify({"status": "error", "message": "缺少必要的参数"}), 400

    try:
        with mysql.connection.cursor() as cursor:
            # 删除好友
            sql_delete_friend = """
                DELETE FROM Friend
                WHERE (Friend_a_id = %s AND Friend_b_id = %s) OR (Friend_a_id = %s AND Friend_b_id = %s)
            """
            cursor.execute(sql_delete_friend, (my_id, search_id, search_id, my_id))
            mysql.connection.commit()

    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

    return jsonify({"status": "success", "message": "好友删除成功"}), 200

# 查询所有好友接口
@bp.route('/getall', methods=['POST'])
def get_all_friends():
    data = request.json
    student_id = data.get('student_id')

    if not student_id:
        return jsonify({"status": "error", "message": "缺少必要的参数"}), 400

    try:
        with mysql.connection.cursor() as cursor:
            # 查询好友的详细信息
            sql_query_friends = """
                SELECT 
                    s.Student_id, 
                    s.Student_name, 
                    s.Student_profileurl, 
                    s.Student_nickname
                FROM 
                    Friend f
                JOIN 
                    Student s 
                ON 
                    (f.Friend_a_id = s.Student_id AND f.Friend_b_id = %s)
                    OR (f.Friend_b_id = s.Student_id AND f.Friend_a_id = %s)
            """
            cursor.execute(sql_query_friends, (student_id, student_id))
            friends = cursor.fetchall()

            # 格式化结果
            friend_list = [
                {
                    "student_id": friend[0],
                    "name": friend[1],
                    "profile_url": friend[2],
                    "nickname": friend[3]
                }
                for friend in friends
            ]

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    return jsonify({
        "status": "success",
        "message": "获取好友列表成功",
        "data": friend_list
    }), 200
