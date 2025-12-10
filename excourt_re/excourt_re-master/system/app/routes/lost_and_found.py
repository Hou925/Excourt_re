from flask import Blueprint, jsonify, request
import psycopg2.extras

from app import get_pg_conn

bp = Blueprint("lost_and_found", __name__, url_prefix="/lost_and_found")


# 用户发布一条自己丢失的物品
@bp.route("/lost/create", methods=["POST"])
def create_lost_item():
    data = request.get_json()
    lost_uploader_id = data.get("Lost_uploader_id")
    lost_item_name = data.get("Lost_item_name")
    lost_description = data.get("Lost_description")
    lost_position = data.get("Lost_position")
    lost_time = data.get("Lost_time")
    lost_contact = data.get("Lost_contact")
    lost_item_pic_url = data.get("Lost_item_pic_url")
    if (
        not lost_uploader_id
        or not lost_item_name
        or not lost_description
        or not lost_position
        or not lost_time
    ):
        return jsonify({"message": "Missing required fields"}), 400
    conn = get_pg_conn()
    cur = conn.cursor()
    try:
        insert_query = """
            INSERT INTO MyLost (
                Lost_uploader_id, Lost_item_name, Lost_description,
                Lost_position, Lost_time, Lost_contact, Lost_item_pic_url
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cur.execute(
            insert_query,
            (
                lost_uploader_id,
                lost_item_name,
                lost_description,
                lost_position,
                lost_time,
                lost_contact,
                lost_item_pic_url,
            ),
        )
        conn.commit()
        return jsonify({"message": "Lost item record created successfully"}), 201
    except Exception as e:
        conn.rollback()
        return (
            jsonify(
                {
                    "message": "Error occurred while creating lost item record",
                    "error": str(e),
                }
            ),
            500,
        )
    finally:
        cur.close()
        conn.close()


@bp.route("/lost/getall", methods=["GET"])
def get_lost_items():
    conn = get_pg_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        query = "SELECT * FROM MyLost"
        cur.execute(query)
        results = cur.fetchall()
        lost_items = [
            {
                "Lost_id": row[0],
                "Lost_uploader_id": row[1],
                "Lost_item_name": row[2],
                "Lost_description": row[3],
                "Lost_position": row[4],
                "Lost_time": row[5].strftime("%Y-%m-%d %H:%M:%S"),
                "Lost_contact": row[6],
                "Lost_item_pic_url": row[7],
            }
            for row in results
        ]
        return jsonify({"lost_items": lost_items}), 200
    except Exception as e:
        return (
            jsonify(
                {"message": "Error occurred while fetching lost items", "error": str(e)}
            ),
            500,
        )
    finally:
        cur.close()
        conn.close()


# 用户找到一个丢失的物品
@bp.route("/found/create", methods=["POST"])
def create_found_item():
    data = request.get_json()
    found_uploader_id = data.get("Found_uploader_id")
    found_item_name = data.get("Found_item_name")
    found_description = data.get("Found_description")
    found_position = data.get("Found_position")
    found_time = data.get("Found_time")
    found_contact = data.get("Found_contact")
    found_item_pic_url = data.get("Found_item_pic_url")
    if (
        not found_uploader_id
        or not found_item_name
        or not found_description
        or not found_position
        or not found_time
    ):
        return jsonify({"message": "Missing required fields"}), 400

    conn = get_pg_conn()
    cur = conn.cursor()
    try:
        insert_query = """
            INSERT INTO MyFound (
                Found_uploader_id, Found_item_name, Found_description,
                Found_position, Found_time, Found_contact, Found_item_pic_url
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cur.execute(
            insert_query,
            (
                found_uploader_id,
                found_item_name,
                found_description,
                found_position,
                found_time,
                found_contact,
                found_item_pic_url,
            ),
        )
        conn.commit()
        return jsonify({"message": "Found item record created successfully"}), 201
    except Exception as e:
        conn.rollback()
        return (
            jsonify(
                {
                    "message": "Error occurred while creating found item record",
                    "error": str(e),
                }
            ),
            500,
        )
    finally:
        cur.close()
        conn.close()


@bp.route("/found/getall", methods=["GET"])
def get_found_items():
    conn = get_pg_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        query = "SELECT * FROM MyFound"
        cur.execute(query)
        results = cur.fetchall()
        found_items = [
            {
                "Found_id": row["Found_id"],
                "Found_uploader_id": row["Found_uploader_id"],
                "Found_item_name": row["Found_item_name"],
                "Found_description": row["Found_description"],
                "Found_position": row["Found_position"],
                "Found_time": row["Found_time"].strftime("%Y-%m-%d %H:%M:%S"),
                "Found_contact": row["Found_contact"],
                "Found_item_pic_url": row["Found_item_pic_url"],
            }
            for row in results
        ]
        return jsonify({"found_items": found_items}), 200
    except Exception as e:
        return (
            jsonify(
                {
                    "message": "Error occurred while fetching found items",
                    "error": str(e),
                }
            ),
            500,
        )
    finally:
        cur.close()
        conn.close()
