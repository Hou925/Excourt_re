from datetime import datetime

from flask import Blueprint, jsonify, request

from app import get_pg_conn

bp = Blueprint("teamup", __name__, url_prefix="/teamup")


@bp.route("/upload", methods=["POST"])
def register_teamup():
    data = request.get_json()
    student_id = data.get("Student_id")
    court_id = data.get("Court_id")
    max_num = data.get("Max_num")
    if not student_id or not court_id or not max_num:
        return jsonify({"message": "Missing required fields"}), 400
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
            (student_id, court_id, student_id, court_id, student_id, court_id),
        )
        result = cur.fetchone()
        if result[0] > 0:
            return (
                jsonify(
                    {
                        "message": "This user has already uploaded a request for this court"
                    }
                ),
                402,
            )
        current_time = datetime.now()
        cur.execute(
            """
            INSERT INTO Teamup_upload (
                Teamup_uploader_id, Teamup_court_id, Teamup_max_num, Teamup_upload_time, Teamup_upload_state
            )
            VALUES (%s, %s, %s, %s, 'not_responsed')
            RETURNING Teamup_upload_id
        """,
            (student_id, court_id, max_num, current_time),
        )
        operation_id = cur.fetchone()[0]
        cur.execute(
            """
            INSERT INTO Operation_record (
                Operator_id, Operation_type, Operation_id, Operation_status, Operation_time
            )
            VALUES (%s, %s, %s, %s, %s)
        """,
            (student_id, "Teamup_upload", operation_id, 0, current_time),
        )
        conn.commit()
        return jsonify({"message": "Teamup registered successfully"}), 201
    except Exception as e:
        conn.rollback()
        return (
            jsonify(
                {"message": "Error occurred while registering teamup", "error": str(e)}
            ),
            500,
        )
    finally:
        cur.close()
        conn.close()


@bp.route("/record", methods=["POST"])
def request_teamup():
    data = request.get_json()
    student_id = data.get("Student_id")
    court_id = data.get("Court_id")
    conn = get_pg_conn()
    cur = conn.cursor()
    try:
        check_query = """
            SELECT 1
            FROM Teamup_request_record
            WHERE Teamup_requester_id = %s AND Teamup_court_id = %s
        """
        cur.execute(check_query, (student_id, court_id))
        if cur.fetchone():
            return jsonify({"message": "重复发送请求"}), 400
        select_query = """
            SELECT Teamup_uploader_id
            FROM Teamup_upload
            WHERE Teamup_court_id = %s
        """
        cur.execute(select_query, (court_id,))
        teamup_upload = cur.fetchone()
        if teamup_upload:
            uploader_id = teamup_upload[0]
            insert_query = """
                INSERT INTO Teamup_request_record (
                    Teamup_requester_id, Teamup_court_id, Teamup_uploader_id, Teamup_request_state
                )
                VALUES (%s, %s, %s, 'not_responsed')
                RETURNING Teamup_request_id
            """
            cur.execute(insert_query, (student_id, court_id, uploader_id))
            Teamup_request_id = cur.fetchone()[0]
            conn.commit()
            return (
                jsonify(
                    {
                        "message": "Teamup request registered successfully",
                        "status": "success",
                    }
                ),
                201,
            )
        else:
            return jsonify({"message": "Court not found"}), 404
    except Exception as e:
        conn.rollback()
        return (
            jsonify(
                {
                    "message": "Error occurred while processing teamup request",
                    "error": str(e),
                }
            ),
            500,
        )
    finally:
        cur.close()
        conn.close()


@bp.route("/get_records", methods=["POST"])
def get_teamup_records():
    data = request.get_json()
    student_id = data.get("Student_id")
    conn = get_pg_conn()
    cur = conn.cursor()
    try:
        select_upload_query = """
            SELECT Teamup_court_id
            FROM Teamup_upload
            WHERE Teamup_uploader_id = %s
        """
        cur.execute(select_upload_query, (student_id,))
        uploads = cur.fetchall()
        matched_records = []
        for upload in uploads:
            court_id = upload[0]
            select_request_query = """
                SELECT *
                FROM Teamup_request_record
                WHERE Teamup_court_id = %s
            """
            cur.execute(select_request_query, (court_id,))
            request_record = cur.fetchall()
            if request_record:
                matched_records.extend(request_record)
        if matched_records:
            return jsonify({"data": matched_records, "status": "success"}), 200
        else:
            return jsonify({"message": "No matched records found"}), 404
    except Exception as e:
        return (
            jsonify(
                {"message": "Error occurred while fetching records", "error": str(e)}
            ),
            500,
        )
    finally:
        cur.close()
        conn.close()


@bp.route("/accept", methods=["POST"])
def update_teamup_state():
    data = request.get_json()
    court_id = data.get("Teamup_court_id")
    teamup_requester_id = data.get("Teamup_requester_id")
    if not court_id or not teamup_requester_id:
        return (
            jsonify({"message": "Court_id and Teamup_requester_id are required"}),
            400,
        )
    conn = get_pg_conn()
    cur = conn.cursor()
    try:
        update_query = """
            UPDATE Teamup_request_record
            SET Teamup_request_state = 'responsed'
            WHERE Teamup_court_id = %s AND Teamup_requester_id = %s
        """
        cur.execute(update_query, (court_id, teamup_requester_id))
        if cur.rowcount > 0:
            select_request_id_query = """
                SELECT Teamup_request_id
                FROM Teamup_request_record
                WHERE Teamup_court_id = %s AND Teamup_requester_id = %s
            """
            cur.execute(select_request_id_query, (court_id, teamup_requester_id))
            teamup_request_id = cur.fetchone()[0]
            update_operation_query = """
                UPDATE Operation_record
                SET Operation_status = 1
                WHERE Operation_id = %s AND Operator_id = %s AND Operation_type = 'Teamup_request'
            """
            cur.execute(
                update_operation_query, (teamup_request_id, teamup_requester_id)
            )
            conn.commit()
            return (
                jsonify(
                    {
                        "message": "Teamup request state updated successfully",
                        "status": "success",
                    }
                ),
                200,
            )
        else:
            return jsonify({"message": "Teamup request not found"}), 404
    except Exception as e:
        conn.rollback()
        return (
            jsonify(
                {
                    "message": "Error occurred while updating teamup request state",
                    "error": str(e),
                }
            ),
            500,
        )
    finally:
        cur.close()
        conn.close()


@bp.route("/refuse", methods=["POST"])
def refuse_teamup_record():
    data = request.get_json()
    court_id = data.get("Teamup_court_id")
    teamup_requester_id = data.get("Teamup_requester_id")
    if not court_id or not teamup_requester_id:
        return (
            jsonify({"message": "Court_id and Teamup_requester_id are required"}),
            400,
        )
    conn = get_pg_conn()
    cur = conn.cursor()
    try:
        update_query = """
            UPDATE Teamup_request_record
            SET Teamup_request_state = 'retrieved'
            WHERE Teamup_court_id = %s AND Teamup_requester_id = %s
        """
        cur.execute(update_query, (court_id, teamup_requester_id))
        if cur.rowcount > 0:
            select_request_id_query = """
                SELECT Teamup_request_id
                FROM Teamup_request_record
                WHERE Teamup_court_id = %s AND Teamup_requester_id = %s
            """
            cur.execute(select_request_id_query, (court_id, teamup_requester_id))
            teamup_request_id = cur.fetchone()[0]
            update_operation_query = """
                UPDATE Operation_record
                SET Operation_status = 2
                WHERE Operation_id = %s AND Operator_id = %s AND Operation_type = 'Teamup_request'
            """
            cur.execute(
                update_operation_query, (teamup_request_id, teamup_requester_id)
            )
            conn.commit()
            return (
                jsonify(
                    {
                        "message": "Teamup request state updated successfully",
                        "status": "success",
                    }
                ),
                200,
            )
        else:
            return jsonify({"message": "Teamup request not found"}), 404
    except Exception as e:
        conn.rollback()
        return (
            jsonify(
                {
                    "message": "Error occurred while updating teamup request state",
                    "error": str(e),
                }
            ),
            500,
        )
    finally:
        cur.close()
        conn.close()


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
            SELECT Teamup_uploader_id FROM Teamup_upload
            WHERE Teamup_court_id = %s
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
