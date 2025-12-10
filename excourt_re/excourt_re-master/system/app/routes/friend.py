from datetime import datetime
import psycopg2.extras

from flask import Blueprint, jsonify, request

from app import get_pg_conn

bp = Blueprint("friend", __name__, url_prefix="/friend")


# 添加好友接口
@bp.route("/add", methods=["POST"])
def add_friend():
    data = request.json
    my_id = data.get("my_id")
    search_id = data.get("search_id")
    if not my_id or not search_id:
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    conn = get_pg_conn()
    cur = conn.cursor()
    try:
        sql_check_friend = """
            SELECT COUNT(*) FROM Friend
            WHERE (Friend_a_id = %s AND Friend_b_id = %s) OR (Friend_a_id = %s AND Friend_b_id = %s)
        """
        cur.execute(sql_check_friend, (my_id, search_id, search_id, my_id))
        if cur.fetchone()[0] > 0:
            return jsonify({"status": "error", "message": "Users are already friends"}), 400
        sql_add_friend = """
            INSERT INTO Friend (Friend_a_id, Friend_b_id) VALUES (%s, %s)
        """
        cur.execute(sql_add_friend, (my_id, search_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cur.close()
        conn.close()
    return jsonify({"status": "success", "message": "Friend added successfully"}), 201


# 删除好友接口
@bp.route("/delete", methods=["POST"])
def delete_friend():
    data = request.json
    my_id = data.get("my_id")
    search_id = data.get("search_id")
    if not my_id or not search_id:
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    conn = get_pg_conn()
    cur = conn.cursor()
    try:
        sql_delete_friend = """
            DELETE FROM Friend
            WHERE (Friend_a_id = %s AND Friend_b_id = %s) OR (Friend_a_id = %s AND Friend_b_id = %s)
        """
        cur.execute(sql_delete_friend, (my_id, search_id, search_id, my_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cur.close()
        conn.close()
    return jsonify({"status": "success", "message": "Friend deleted successfully"}), 200


# 查询所有好友接口
@bp.route("/getall", methods=["POST"])
def get_all_friends():
    data = request.json
    student_id = data.get("student_id")
    if not student_id:
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    conn = get_pg_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
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
        cur.execute(sql_query_friends, (student_id, student_id))
        friends = cur.fetchall()
        friend_list = [
            {
                "student_id": friend["Student_id"],
                "name": friend["Student_name"],
                "profile_url": friend["Student_profileurl"],
                "nickname": friend["Student_nickname"],
            }
            for friend in friends
        ]
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cur.close()
        conn.close()
    return (
        jsonify(
            {"status": "success", "message": "Friend list fetched successfully", "data": friend_list}
        ),
        200,
    )
