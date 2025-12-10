from datetime import datetime
import psycopg2.extras

from flask import Blueprint, jsonify, request

import requests

from app import get_pg_conn

bp = Blueprint("exchangecourt", __name__, url_prefix="/exchangecourt")


@bp.route("/upload", methods=["POST"])
def add_exchange_upload_and_operation_record():
    data = request.get_json()
    exchange_uploader_id = data.get("Exchange_uploader_id")
    exchange_uploaded_court_id = data.get("Exchange_uploaded_court_id")
    if not exchange_uploader_id or not exchange_uploaded_court_id:
        return jsonify({"message": "Missing required fields"}), 400
    current_time = datetime.now()
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
            (
                exchange_uploader_id,
                exchange_uploaded_court_id,
                exchange_uploader_id,
                exchange_uploaded_court_id,
                exchange_uploader_id,
                exchange_uploaded_court_id,
            ),
        )
        result = cur.fetchone()
        if result[0] > 0:
            return (
                jsonify(
                    {
                        "message": "This user has already uploaded a request for this court"
                    }
                ),
                409,
            )
        insert_exchange_query = """
            INSERT INTO Exchangecourt_upload (
                Exchange_uploader_id, Exchange_upload_state,
                Exchange_uploaded_court_id, Exchange_upload_time
            )
            VALUES (%s, %s, %s, %s)
            RETURNING Exchange_upload_id
        """
        cur.execute(
            insert_exchange_query,
            (
                exchange_uploader_id,
                "not_responsed",
                exchange_uploaded_court_id,
                current_time,
            ),
        )
        exchangecourt_upload_id = cur.fetchone()[0]
        insert_operation_query = """
            INSERT INTO Operation_record (
                Operator_id, Operation_type, Operation_id,
                Operation_status, Operation_time
            )
            VALUES (%s, %s, %s, %s, %s)
        """
        operation_type = "Exchangecourt_upload"
        operation_status = 0
        cur.execute(
            insert_operation_query,
            (
                exchange_uploader_id,
                operation_type,
                exchangecourt_upload_id,
                operation_status,
                current_time,
            ),
        )
        conn.commit()
        return (
            jsonify(
                {"message": "Exchange upload and operation record added successfully"}
            ),
            201,
        )
    except Exception as e:
        conn.rollback()
        return (
            jsonify(
                {"message": "Error occurred while adding records", "error": str(e)}
            ),
            500,
        )
    finally:
        cur.close()
        conn.close()


@bp.route("/respond", methods=["POST"])
def respond_to_exchange():
    data = request.get_json()
    exchange_responser_id = data.get("Exchange_responser_id")
    exchange_uploader_court_id = data.get("Exchange_uploader_court_id")
    exchange_responser_court_id = data.get("Exchange_responser_court_id")

    if not all(
        [exchange_responser_id, exchange_uploader_court_id, exchange_responser_court_id]
    ):
        return jsonify({"message": "Missing required fields"}), 400

    conn = get_pg_conn()
    cur = conn.cursor()
    current_time = datetime.now()
    try:
        check_uploader_query = """
            SELECT Exchange_uploader_id FROM Exchangecourt_upload 
            WHERE Exchange_uploaded_court_id = %s
        """
        cur.execute(check_uploader_query, (exchange_uploader_court_id,))
        uploader_record = cur.fetchone()
        if not uploader_record:
            return (
                jsonify({"message": "No exchange uploader found for the given court."}),
                404,
            )
        exchange_uploader_id = uploader_record[0]
        check_offer_query = """
            SELECT 1 FROM Offercourt_upload 
            WHERE Offer_uploader_id = %s 
            AND Offer_uploaded_court_id = %s
        """
        check_teamup_query = """
            SELECT 1 FROM Teamup_upload 
            WHERE Teamup_uploader_id = %s 
            AND Teamup_court_id = %s
        """
        cur.execute(
            check_offer_query, (exchange_responser_id, exchange_responser_court_id)
        )
        offer_record = cur.fetchone()
        cur.execute(
            check_teamup_query, (exchange_responser_id, exchange_responser_court_id)
        )
        teamup_record = cur.fetchone()
        if offer_record or teamup_record:
            return (
                jsonify(
                    {
                        "message": "Duplicate upload request found. Please do not submit multiple upload requests for the same court."
                    }
                ),
                402,
            )
        check_exchange_query = """
            SELECT * FROM Exchangecourt_upload 
            WHERE Exchange_uploader_id = %s 
            AND Exchange_uploaded_court_id = %s
        """
        cur.execute(
            check_exchange_query, (exchange_uploader_id, exchange_uploader_court_id)
        )
        upload_record = cur.fetchone()
        if not upload_record:
            insert_upload_query = """
                INSERT INTO Exchangecourt_upload (
                    Exchange_uploader_id, Exchange_uploaded_court_id,
                    Exchange_upload_state, Exchange_upload_time
                ) VALUES (%s, %s, %s, %s)
            """
            cur.execute(
                insert_upload_query,
                (
                    exchange_uploader_id,
                    exchange_uploader_court_id,
                    "not_responsed",
                    current_time,
                ),
            )
            conn.commit()
        insert_record_query = """
            INSERT INTO Exchangecourt_record (
                Exchange_uploader_id, Exchange_responser_id,
                Exchange_uploader_court_id, Exchange_responser_court_id,
                Exchange_state
            )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING Exchange_record_id
        """
        cur.execute(
            insert_record_query,
            (
                exchange_uploader_id,
                exchange_responser_id,
                exchange_uploader_court_id,
                exchange_responser_court_id,
                "not_responsed",
            ),
        )
        exchangecourt_record_id = cur.fetchone()[0]
        insert_operation_query = """
            INSERT INTO Operation_record (
                Operator_id, Operation_type, Operation_id,
                Operation_status, Operation_time
            )
            VALUES (%s, %s, %s, %s, %s)
        """
        operation_type = "Exchangecourt_record"
        operation_status = 0
        cur.execute(
            insert_operation_query,
            (
                exchange_responser_id,
                operation_type,
                exchangecourt_record_id,
                operation_status,
                current_time,
            ),
        )
        conn.commit()
        return jsonify({"message": "Exchange response recorded successfully"}), 201
    except Exception as e:
        conn.rollback()
        return (
            jsonify(
                {
                    "message": "Error occurred while recording exchange response",
                    "error": str(e),
                }
            ),
            500,
        )
    finally:
        cur.close()
        conn.close()


@bp.route("/get_response_records_by_student", methods=["POST"])
def get_response_records_by_student():
    data = request.get_json()
    student_id = data.get("student_id")
    if not student_id:
        return jsonify({"message": "Missing required fields"}), 400

    conn = get_pg_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        query = """
            SELECT er.Exchange_record_id, er.Exchange_state, er.Exchange_uploader_court_id, er.Exchange_responser_court_id,
                   er.Exchange_uploader_score, er.Exchange_responser_score,er.Exchange_responser_id,
                   s.Student_name, s.Student_profileurl, s.Student_nickname, s.Student_credit, s.Student_level
            FROM Exchangecourt_record er
            JOIN Student s ON er.Exchange_responser_id = s.Student_id
            WHERE er.Exchange_uploader_id = %s
        """
        cur.execute(query, (student_id,))
        response_records = cur.fetchall()
        response_records_list = [
            {
                "exchange_record_id": row[0],
                "exchange_state": row[1],
                "exchange_uploader_court_id": row[2],
                "exchange_responser_court_id": row[3],
                "exchange_uploader_score": row[4],
                "exchange_responser_score": row[5],
                "exchange_responser_id": row[6],
                "responser_info": {
                    "name": row[7],
                    "profileurl": row[8],
                    "nickname": row[9],
                    "credit": row[10],
                    "level": row[11],
                },
            }
            for row in response_records
        ]
        return jsonify({"data": response_records_list, "status": "success"}), 200
    except Exception as e:
        conn.rollback()
        return (
            jsonify(
                {
                    "message": "Error occurred while fetching response records",
                    "error": str(e),
                }
            ),
            500,
        )
    finally:
        cur.close()
        conn.close()


@bp.route("/complete_exchange", methods=["POST"])
def complete_exchange():
    data = request.get_json()
    uploader_court_id = data.get("Exchange_uploader_court_id")
    responser_court_id = data.get("Exchange_responser_court_id")
    uploader_id = data.get("Exchange_uploader_id")
    responser_id = data.get("Exchange_responser_id")

    if (
        not uploader_court_id
        or not responser_court_id
        or not uploader_id
        or not responser_id
    ):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    conn = get_pg_conn()
    cur = conn.cursor()
    try:
        sql_update_record = """
            UPDATE Exchangecourt_record
            SET Exchange_state = 'exchanged'
            WHERE Exchange_uploader_court_id = %s 
              AND Exchange_responser_court_id = %s
              AND Exchange_uploader_id = %s
              AND Exchange_responser_id = %s
        """
        cur.execute(
            sql_update_record,
            (uploader_court_id, responser_court_id, uploader_id, responser_id),
        )
        if cur.rowcount == 0:
            return jsonify({"status": "error", "message": "No matching exchange record found"}), 404
        sql_update_upload = """
            UPDATE Exchangecourt_upload
            SET Exchange_upload_state = 'exchanged'
            WHERE Exchange_uploaded_court_id = %s
              AND Exchange_uploader_id = %s
        """
        cur.execute(sql_update_upload, (uploader_court_id, uploader_id))
        if cur.rowcount == 0:
            return jsonify({"status": "error", "message": "No matching upload record found"}), 404
        
        swap_url = "http://localhost:5000/courts/swap_owner"
        payload = {
            "court_id_1": uploader_court_id,
            "new_owner_1": responser_id,
            "court_id_2": responser_court_id,
            "new_owner_2": uploader_id
        }
        try:
            resp = requests.post(swap_url, json=payload, timeout=5)
            if resp.status_code != 200 or resp.json().get("status") != "success":
                raise Exception(f"Swap owner failed: {resp.text}")
        except Exception as e:
            conn.rollback()
            return jsonify({"status": "error", "message": f"交换场地主人失败: {str(e)}"}), 500
        
        conn.commit()
        return jsonify({"status": "success", "message": "Exchange completed successfully"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cur.close()
        conn.close()


@bp.route("/refuse", methods=["POST"])
def refuse_exchange():
    data = request.get_json()
    uploader_court_id = data.get("Exchange_uploader_court_id")
    responser_court_id = data.get("Exchange_responser_court_id")
    uploader_id = data.get("Exchange_uploader_id")
    responser_id = data.get("Exchange_responser_id")

    if (
        not uploader_court_id
        or not responser_court_id
        or not uploader_id
        or not responser_id
    ):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    conn = get_pg_conn()
    cur = conn.cursor()
    try:
        sql_update_record = """
            UPDATE Exchangecourt_record
            SET Exchange_state = 'retrieved'
            WHERE Exchange_uploader_court_id = %s 
              AND Exchange_responser_court_id = %s
              AND Exchange_uploader_id = %s
              AND Exchange_responser_id = %s
        """
        cur.execute(
            sql_update_record,
            (uploader_court_id, responser_court_id, uploader_id, responser_id),
        )
        if cur.rowcount == 0:
            return jsonify({"status": "error", "message": "No matching record found"}), 404
        conn.commit()
        return jsonify({"status": "success", "message": "Exchange refused successfully"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cur.close()
        conn.close()
