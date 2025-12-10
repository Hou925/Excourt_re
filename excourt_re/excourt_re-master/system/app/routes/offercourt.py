from datetime import datetime

from flask import Blueprint, jsonify, request

import requests

from app import get_pg_conn

bp = Blueprint("offercourt", __name__, url_prefix="/offercourt")


@bp.route("/upload", methods=["POST"])
def offer_court():
    data = request.json
    my_id = data.get("my_id")
    court_id = data.get("court_id")
    upload_time = data.get("upload_time", datetime.now())
    if not my_id or not court_id:
        return jsonify({"status": "error", "message": "缺少必要的参数"}), 400
    conn = get_pg_conn()
    cur = conn.cursor()
    try:
        check_existing_upload_query = """
            SELECT COUNT(*) 
            FROM (
                SELECT 1 FROM Exchangecourt_upload WHERE Exchange_uploader_id = %s AND Exchange_uploaded_court_id = %s
                UNION
                SELECT 1 FROM Offercourt_upload WHERE Offer_uploader_id = %s AND Offer_uploaded_court_id = %s
                UNION
                SELECT 1 FROM Teamup_upload WHERE Teamup_uploader_id = %s AND Teamup_court_id = %s
            ) AS existing_uploads
        """
        cur.execute(
            check_existing_upload_query,
            (my_id, court_id, my_id, court_id, my_id, court_id),
        )
        result = cur.fetchone()
        if result[0] > 0:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "This user has already uploaded a request for this court",
                    }
                ),
                402,
            )
        sql_offer = """
            INSERT INTO Offercourt_upload 
            (Offer_uploader_id, Offer_uploaded_court_id, Offer_upload_time, Offer_upload_state) 
            VALUES (%s, %s, %s, 'not_responsed')
            RETURNING Offer_upload_id
        """
        cur.execute(sql_offer, (my_id, court_id, upload_time))
        offer_upload_id = cur.fetchone()[0]
        sql_operation = """
            INSERT INTO Operation_record 
            (Operator_id, Operation_type, Operation_id, Operation_status, Operation_time) 
            VALUES (%s, 'Offercourt_upload', %s, 0, %s)
        """
        cur.execute(sql_operation, (my_id, offer_upload_id, upload_time))
        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cur.close()
        conn.close()
    return (
        jsonify(
            {
                "status": "success",
                "message": "送场发布成功",
                "data": {"Offer_upload_id": offer_upload_id},
            }
        ),
        201,
    )


@bp.route("/record", methods=["POST"])
def accept_court():
    data = request.json
    my_id = data.get("my_id")
    court_id = data.get("court_id")
    upload_time = data.get("upload_time", datetime.now())
    if not my_id or not court_id:
        return jsonify({"status": "error", "message": "缺少必要的参数"}), 400
    conn = get_pg_conn()
    cur = conn.cursor()
    try:
        sql_find = """
            SELECT Offer_uploader_id FROM Offercourt_upload 
            WHERE Offer_uploaded_court_id = %s AND (offer_upload_state = 'not_responsed' or offer_upload_state = 'responsed')
        """
        cur.execute(sql_find, (court_id,))
        offer_uploader_id = cur.fetchone()
        if offer_uploader_id is None:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "No pending offer found for this court",
                    }
                ),
                404,
            )
        sql_check = """
            SELECT COUNT(*) FROM Offercourt_record 
            WHERE Offer_uploader_id = %s AND Offer_responser_id = %s AND Offer_uploader_court_id = %s AND Offer_state != 'retrieved'
        """
        cur.execute(sql_check, (offer_uploader_id[0], my_id, court_id))
        existing_record_count = cur.fetchone()[0]
        if existing_record_count > 0:
            return (
                jsonify({"status": "error", "message": "已经存在相同的送场记录"}),
                409,
            )
        sql_accept = """
            INSERT INTO Offercourt_record 
            (Offer_uploader_id, Offer_responser_id, Offer_state, Offer_uploader_court_id) 
            VALUES (%s, %s, 'not_responsed', %s)
            RETURNING Offer_record_id
        """
        cur.execute(sql_accept, (offer_uploader_id[0], my_id, court_id))
        accept_record_id = cur.fetchone()[0]
        sql_update = """
            UPDATE Offercourt_upload SET Offer_upload_state = 'responsed' WHERE Offer_uploaded_court_id = %s AND Offer_uploader_id = %s
        """
        cur.execute(sql_update, (court_id, offer_uploader_id[0]))
        sql_operation = """
            INSERT INTO Operation_record 
            (Operator_id, Operation_type, Operation_id, Operation_status, Operation_time) 
            VALUES (%s, 'Request_court', %s, 0, %s)
        """
        cur.execute(sql_operation, (my_id, accept_record_id, upload_time))
        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cur.close()
        conn.close()
    return (
        jsonify(
            {
                "status": "success",
                "message": "送场接受成功",
                "data": {"Accept_record_id": accept_record_id},
            }
        ),
        201,
    )


@bp.route("/accept", methods=["POST"])
def accept_offer():
    data = request.json
    my_id = data.get("my_id")
    court_id = data.get("court_id")
    recorder_id = data.get("recorder_id")
    if not my_id or not court_id or not recorder_id:
        return jsonify({"status": "error", "message": "缺少必要的参数"}), 400
    conn = get_pg_conn()
    cur = conn.cursor()
    try:
        sql_find_record_id = """
            SELECT Offer_record_id FROM Offercourt_record
            WHERE Offer_uploader_id = %s AND Offer_responser_id = %s AND Offer_uploader_court_id = %s
        """
        cur.execute(sql_find_record_id, (my_id, recorder_id, court_id))
        result = cur.fetchone()
        if result is None:
            return jsonify({"status": "error", "message": "没有找到匹配的记录"}), 404
        offer_record_id = result[0]
        
        sql_find_offer_responser = """
            SELECT offer_responser_id FROM Offercourt_record
            WHERE offer_record_id = %s
        """
        cur.execute(sql_find_offer_responser, (offer_record_id,))
        row = cur.fetchone()
        if row is None:
            return jsonify({"status": "error", "message": "找不到对应的送场记录"}), 404
        new_owner_id = row[0]
        
        
        sql_update_record = """
            UPDATE Offercourt_record
            SET Offer_state = 'offered'
            WHERE Offer_record_id = %s
        """
        cur.execute(sql_update_record, (offer_record_id,))
        sql_update_operation = """
            UPDATE Operation_record
            SET Operation_status = 1
            WHERE Operation_id = %s AND Operation_type = 'Request_court' AND Operator_id = %s
        """
        cur.execute(sql_update_operation, (offer_record_id, recorder_id))
        
        url = "http://localhost:5000/courts/update_owner"
        payload = {
            "court_id": court_id,
            "new_owner_id": new_owner_id
        }
        resp = requests.post(url, json=payload, timeout=5)
        if resp.status_code != 200 or resp.json().get("status") != "success":
            raise Exception(f"5000端口更改场主失败: {resp.text}")
                
        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cur.close()
        conn.close()
    return jsonify({"status": "success", "message": "送场接受成功"}), 200


@bp.route("/decline", methods=["POST"])
def decline_offer():
    data = request.json
    my_id = data.get("my_id")
    court_id = data.get("court_id")
    recorder_id = data.get("recorder_id")
    if not my_id or not court_id or not recorder_id:
        return jsonify({"status": "error", "message": "缺少必要的参数"}), 400
    conn = get_pg_conn()
    cur = conn.cursor()
    try:
        sql_find_record_id = """
            SELECT Offer_record_id FROM Offercourt_record 
            WHERE Offer_uploader_id = %s AND Offer_responser_id = %s AND Offer_uploader_court_id = %s
        """
        cur.execute(sql_find_record_id, (my_id, recorder_id, court_id))
        result = cur.fetchone()
        if result is None:
            return jsonify({"status": "error", "message": "没有找到匹配的记录"}), 404
        offer_record_id = result[0]
        sql_update = """
            UPDATE Offercourt_record
            SET Offer_state = 'retrieved'
            WHERE Offer_record_id = %s
        """
        cur.execute(sql_update, (offer_record_id,))
        sql_update_operation = """
            UPDATE Operation_record
            SET Operation_status = 2
            WHERE Operation_id = %s AND Operation_type = 'Request_court' AND Operator_id = %s
        """
        cur.execute(sql_update_operation, (offer_record_id, recorder_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cur.close()
        conn.close()
    return jsonify({"status": "success", "message": "送场请求已拒绝"}), 200


@bp.route("/get_offer_records", methods=["POST"])
def get_all_records():
    data = request.json
    my_id = data.get("my_id")
    if not my_id:
        return jsonify({"status": "error", "message": "缺少必要的参数"}), 400
    conn = get_pg_conn()
    cur = conn.cursor()
    try:
        sql_query_records = """
            SELECT Offer_record_id, Offer_responser_id, Offer_state, Offer_uploader_court_id
            FROM Offercourt_record
            WHERE Offer_uploader_id = %s
        """
        cur.execute(sql_query_records, (my_id,))
        records = cur.fetchall()
        if not records:
            return (
                jsonify({"status": "success", "message": "没有找到记录", "data": []}),
                200,
            )
        responser_ids = [record[1] for record in records]
        if not responser_ids:
            return (
                jsonify({"status": "success", "message": "没有找到记录", "data": []}),
                200,
            )
        placeholders = ",".join(["%s"] * len(responser_ids))
        sql_query_students = f"""
            SELECT Student_id, Student_name, Student_profileurl, Student_nickname, Student_credit, Student_level, Student_status
            FROM Student
            WHERE Student_id IN ({placeholders})
        """
        cur.execute(sql_query_students, responser_ids)
        students_info = cur.fetchall()
        students_dict = {student[0]: student for student in students_info}
        enriched_records = []
        for record in records:
            student_info = students_dict.get(record[1])
            if student_info:
                enriched_record = {
                    "Offer_record_id": record[0],
                    "Offer_responser_id": record[1],
                    "Offer_state": record[2],
                    "Offer_uploader_court_id": record[3],
                    "Student_name": student_info[1],
                    "Student_profileurl": student_info[2],
                    "Student_nickname": student_info[3],
                    "Student_credit": student_info[4],
                    "Student_level": student_info[5],
                    "Student_status": student_info[6],
                }
                enriched_records.append(enriched_record)
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cur.close()
        conn.close()
    return (
        jsonify(
            {"status": "success", "message": "获取记录成功", "data": enriched_records}
        ),
        200,
    )


@bp.route("/get_uploader_id", methods=["POST"])
def get_uploader_id():
    data = request.json
    court_id = data.get("court_id")
    if not court_id:
        return jsonify({"status": "error", "message": "Missing court_id"}), 400
    conn = get_pg_conn()
    cur = conn.cursor()
    try:
        sql_query = """
            SELECT Offer_uploader_id FROM Offercourt_upload
            WHERE Offer_uploaded_court_id = %s
        """
        cur.execute(sql_query, (court_id,))
        result = cur.fetchone()
        if result:
            return (
                jsonify({"status": "success", "data": {"uploader_id": result[0]}}),
                200,
            )
        else:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "No pending offer found for this court",
                    }
                ),
                404,
            )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cur.close()
        conn.close()
