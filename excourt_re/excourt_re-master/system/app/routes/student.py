from datetime import datetime

from flask import Blueprint, jsonify, request

from app import get_pg_conn

bp = Blueprint("student", __name__, url_prefix="/student")


@bp.route("/register", methods=["POST"])
def register_student():
    data = request.get_json()
    student_id = data.get("Student_id")
    student_name = data.get("Student_name")
    student_nickname = data.get("Student_nickname")
    student_phone = data.get("Student_phone")
    student_password = data.get("Student_password")

    if (
        not student_id
        or not student_name
        or not student_password
        or not student_nickname
    ):
        return jsonify({"message": "Missing required fields"}), 400

    conn = get_pg_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO Student (
                Student_id, Student_name, Student_nickname, Student_phone,
                Student_password, Student_credit, Student_level, Student_status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
            (
                student_id,
                student_name,
                student_nickname,
                student_phone,
                student_password,
                100,
                1,
                1,
            ),
        )
        conn.commit()
        return jsonify({"message": "Student registered successfully"}), 201
    except Exception as e:
        conn.rollback()
        return (
            jsonify(
                {"message": "Error occurred while registering student", "error": str(e)}
            ),
            500,
        )
    finally:
        cur.close()
        conn.close()


@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    student_id = data.get("Student_id")
    password = data.get("Student_password")

    if not student_id or not password:
        return jsonify({"message": "Student_id and password are required"}), 400

    conn = get_pg_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT Student_password FROM Student WHERE Student_id = %s", (student_id,)
        )
        result = cur.fetchone()
        if not result:
            return jsonify({"message": "Student_id not found"}), 404

        if result[0] != password:
            return jsonify({"message": "Incorrect password"}), 401

        cur.execute(
            "SELECT Student_id, Student_name FROM Student WHERE Student_id = %s",
            (student_id,),
        )
        student = cur.fetchone()
        return jsonify(
            {
                "message": "Login successful",
                "Student_id": student[0],
                "Student_name": student[1],
            }
        )
    finally:
        cur.close()
        conn.close()


@bp.route("/update", methods=["POST"])
def update_info():
    data = request.get_json()
    search_id = data.get("search_id")
    profileurl = data.get("profileurl")
    nickname = data.get("nickname")
    phone = data.get("phone")
    level = data.get("level")

    if not search_id or not nickname or not phone or not level:
        return jsonify({"status": "error", "message": "缺少必要的参数"}), 400

    conn = get_pg_conn()
    cur = conn.cursor()
    try:
        sql_update_student = """
            UPDATE Student
            SET Student_profileurl = %s, Student_nickname = %s, Student_phone = %s, Student_level = %s
            WHERE Student_id = %s
        """
        cur.execute(sql_update_student, (profileurl, nickname, phone, level, search_id))
        conn.commit()
        return jsonify({"status": "success", "message": "用户信息已更新"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cur.close()
        conn.close()


@bp.route("/owned-courts", methods=["POST"])
def get_owned_courts():
    data = request.get_json()
    student_id = data.get("student_id")
    if not student_id:
        return jsonify({"message": "Missing required field: student_id"}), 400

    conn = get_pg_conn()
    cur = conn.cursor()
    try:
        query = """
            SELECT Court_id, Court_no, Court_campus, Court_date, Court_time, Court_owner
            FROM CourtInfo
            WHERE Court_owner = %s AND Court_state = 'owned'
        """
        cur.execute(query, (student_id,))
        results = cur.fetchall()
        today = datetime.today().date()
        owned_courts = [
            {
                "dayId": (
                    (row[3] - today).days
                    if isinstance(row[3], datetime)
                    else (row[3] - today).days
                ),
                "Court_owner": row[5],
                "Court_no": row[1],
                "Court_time": row[4],
                "Court_id": row[0],
            }
            for row in results
        ]
        return jsonify({"student_id": student_id, "owned_courts": owned_courts}), 200
    except Exception as e:
        return (
            jsonify(
                {
                    "message": "Error occurred while fetching owned courts",
                    "error": str(e),
                }
            ),
            500,
        )
    finally:
        cur.close()
        conn.close()


@bp.route("/get_operation_records", methods=["GET"])
def get_operation_records():
    data = request.get_json()
    operator_id = data.get("student_id")

    if not operator_id:
        return jsonify({"message": "Missing required fields"}), 400

    conn = get_pg_conn()
    cur = conn.cursor()
    try:
        query = """
            SELECT Operation_record_id, Operation_type, Operation_id, Operation_status, Operation_time
            FROM Operation_record
            WHERE Operator_id = %s
            ORDER BY Operation_time DESC
        """
        cur.execute(query, (operator_id,))
        operation_records = cur.fetchall()
        operation_records_list = [
            {
                "operation_record_id": row[0],
                "operation_type": row[1],
                "operation_id": row[2],
                "operation_status": row[3],
                "operation_time": row[4].strftime("%Y-%m-%d %H:%M:%S"),
            }
            for row in operation_records
        ]

        return jsonify(operation_records_list), 200
    except Exception as e:
        conn.rollback()
        return (
            jsonify(
                {
                    "message": "Error occurred while fetching operation records",
                    "error": str(e),
                }
            ),
            500,
        )
    finally:
        cur.close()
        conn.close()


@bp.route("/find", methods=["POST"])
def query_friend():
    search_id = request.json.get("search_id")
    if not search_id:
        return jsonify({"status": "error", "message": "缺少必要的参数"}), 400

    conn = get_pg_conn()
    cur = conn.cursor()
    try:
        sql_query_student = """
            SELECT Student_id, Student_name, Student_profileurl, Student_nickname, Student_credit, Student_level, Student_status
                ,Student_phone
            FROM Student
            WHERE Student_id = %s
        """
        cur.execute(sql_query_student, (search_id,))
        user_info = cur.fetchone()

        if not user_info:
            return jsonify({"status": "error", "message": "用户不存在"}), 404

        return (
            jsonify(
                {"status": "success", "message": "获取用户信息成功", "data": user_info}
            ),
            200,
        )
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cur.close()
        conn.close()


@bp.route("/get_exchangecourt", methods=["POST"])
def get_exchangecourt():
    data = request.get_json()
    my_id = data.get("my_id")
    if not my_id:
        return jsonify({"message": "Missing required fields: my_id"}), 400

    conn = get_pg_conn()
    cur = conn.cursor()
    try:
        query = """
            SELECT Exchange_uploaded_court_id AS court_id
            FROM Exchangecourt_upload
            WHERE Exchange_uploader_id != %s
        """
        cur.execute(query, (my_id,))
        court_ids = cur.fetchall()
        court_ids_list = [{"court_id": row[0]} for row in court_ids]
        return jsonify({"court_ids_list": court_ids_list}), 200
    except Exception as e:
        conn.rollback()
        return (
            jsonify(
                {"message": "Error occurred while fetching court ids", "error": str(e)}
            ),
            500,
        )
    finally:
        cur.close()
        conn.close()


@bp.route("/get_teamupcourt", methods=["POST"])
def get_teamupcourt():
    data = request.get_json()
    my_id = data.get("my_id")
    if not my_id:
        return jsonify({"message": "Missing required fields: my_id"}), 400

    conn = get_pg_conn()
    cur = conn.cursor()
    try:
        query = """
            SELECT Teamup_court_id AS court_id
            FROM Teamup_upload
            WHERE Teamup_uploader_id != %s
        """
        cur.execute(query, (my_id,))
        court_ids = cur.fetchall()
        court_ids_list = [{"court_id": row[0]} for row in court_ids]
        return jsonify({"court_ids_list": court_ids_list}), 200
    except Exception as e:
        conn.rollback()
        return (
            jsonify(
                {"message": "Error occurred while fetching court ids", "error": str(e)}
            ),
            500,
        )
    finally:
        cur.close()
        conn.close()


@bp.route("/get_offercourt", methods=["POST"])
def get_offercourt():
    data = request.get_json()
    my_id = data.get("my_id")
    if not my_id:
        return jsonify({"message": "Missing required fields: my_id"}), 400

    conn = get_pg_conn()
    cur = conn.cursor()
    try:
        query = """
            SELECT Offer_uploaded_court_id AS court_id
            FROM Offercourt_upload
            WHERE Offer_uploader_id != %s AND (offer_upload_state = 'not_responsed' or offer_upload_state = 'responsed')
        """
        cur.execute(query, (my_id,))
        court_ids = cur.fetchall()
        court_ids_list = [{"court_id": row[0]} for row in court_ids]
        return jsonify({"court_ids_list": court_ids_list}), 200
    except Exception as e:
        conn.rollback()
        return (
            jsonify(
                {"message": "Error occurred while fetching court ids", "error": str(e)}
            ),
            500,
        )
    finally:
        cur.close()
        conn.close()


@bp.route("/get_apply", methods=["POST"])
def get_user_apply():
    data = request.get_json()
    my_id = data.get("my_id")
    if not my_id:
        return jsonify({"message": "Missing required fields: my_id"}), 400

    conn = get_pg_conn()
    cur = conn.cursor()
    try:
        query1 = """
            SELECT Exchange_uploaded_court_id AS court_id, Exchange_upload_state AS status, 'Exchangecourt' AS source
            FROM Exchangecourt_upload
            WHERE Exchange_uploader_id = %s
        """
        cur.execute(query1, (my_id,))
        exchangecourt_data = cur.fetchall()

        query2 = """
            SELECT Offer_uploaded_court_id AS court_id, Offer_upload_state AS status, 'Offercourt' AS source
            FROM Offercourt_upload
            WHERE Offer_uploader_id = %s
        """
        cur.execute(query2, (my_id,))
        offercourt_data = cur.fetchall()

        query3 = """
            SELECT Teamup_court_id AS court_id, Teamup_upload_state AS status, 'Teamup' AS source
            FROM Teamup_upload
            WHERE Teamup_uploader_id = %s
        """
        cur.execute(query3, (my_id,))
        teamup_data = cur.fetchall()

        result = [
            {"court_id": row[0], "status": row[1], "source": row[2]}
            for row in exchangecourt_data + offercourt_data + teamup_data
        ]

        return jsonify({"status": "success", "data": result}), 200
    except Exception as e:
        conn.rollback()
        return (
            jsonify(
                {"message": "Error occurred while fetching court ids", "error": str(e)}
            ),
            500,
        )
    finally:
        cur.close()
        conn.close()


@bp.route("/get_my_request", methods=["POST"])
def get_user_repond():
    data = request.get_json()
    my_id = data.get("my_id")
    if not my_id:
        return jsonify({"message": "Missing required fields: my_id"}), 400

    conn = get_pg_conn()
    cur = conn.cursor()
    try:
        query = """
            SELECT Exchange_responser_court_id AS court_id,Exchange_state AS status, 'Exchangecourt' AS source
            FROM Exchangecourt_record
            WHERE Exchange_responser_id = %s
        """
        cur.execute(query, (my_id,))
        exchangecourt_data = cur.fetchall()

        query = """
            SELECT Offer_uploader_court_id AS court_id,Offer_state AS status, 'Offercourt' AS source
            FROM Offercourt_record
            WHERE Offer_responser_id = %s
        """
        cur.execute(query, (my_id,))
        offercourt_data = cur.fetchall()

        query = """
            SELECT Teamup_court_id AS court_id,Teamup_request_state AS status, 'Teamup' AS source
            FROM Teamup_request_record
            WHERE Teamup_requester_id = %s
        """
        cur.execute(query, (my_id,))
        teamup_data = cur.fetchall()

        result = [
            {"court_id": row[0], "status": row[1], "source": row[2]}
            for row in exchangecourt_data + offercourt_data + teamup_data
        ]
        return jsonify({"status": "success", "data": result}), 200
    except Exception as e:
        conn.rollback()
        return (
            jsonify(
                {"message": "Error occurred while fetching court ids", "error": str(e)}
            ),
            500,
        )
    finally:
        cur.close()
        conn.close()


@bp.route("/delete_apply", methods=["POST"])
def delete_apply():
    data = request.get_json()
    table_name = data.get("table_name")
    court_id = data.get("court_id")
    applier_id = data.get("applier_id")

    if not table_name or not court_id or not applier_id:
        return (
            jsonify(
                {
                    "message": "Missing required fields: table_name, court_id or uploader_id"
                }
            ),
            400,
        )

    table_deletes = {
        "Exchangecourt": {
            "query": """
                DELETE FROM Exchangecourt_record
                WHERE Exchange_responser_court_id = %s AND Exchange_responser_id = %s
            """
        },
        "Offercourt": {
            "query": """
                DELETE FROM Offercourt_record
                WHERE Offer_uploader_court_id = %s AND Offer_responser_id = %s
            """
        },
        "Teamup": {
            "query": """
                DELETE FROM Teamup_request_record
                WHERE Teamup_court_id = %s AND Teamup_requester_id = %s
            """
        },
    }

    if table_name not in table_deletes:
        return jsonify({"message": f"Invalid table name: {table_name}"}), 400

    query = table_deletes[table_name]["query"]

    conn = get_pg_conn()
    cur = conn.cursor()
    try:
        cur.execute(query, (court_id, applier_id))
        conn.commit()
        if cur.rowcount == 0:
            return (
                jsonify(
                    {
                        "status": "failure",
                        "message": "No matching records found to delete",
                    }
                ),
                404,
            )
        return (
            jsonify({"status": "success", "message": "Record deleted successfully"}),
            200,
        )
    except Exception as e:
        conn.rollback()
        return (
            jsonify(
                {"message": "Error occurred while deleting record", "error": str(e)}
            ),
            500,
        )
    finally:
        cur.close()
        conn.close()


@bp.route("/delete_pub", methods=["POST"])
def delete_pub():
    data = request.get_json()
    table_name = data.get("table_name")
    court_id = data.get("court_id")
    puber_id = data.get("puber_id")
    if not table_name or not court_id or not puber_id:
        return (
            jsonify(
                {
                    "message": "Missing required fields: table_name, court_id or uploader_id"
                }
            ),
            400,
        )

    table_deletes = {
        "Exchangecourt": {
            "query": """
                DELETE FROM Exchangecourt_upload
                WHERE Exchange_uploaded_court_id = %s AND Exchange_uploader_id = %s
            """
        },
        "Offercourt": {
            "query": """
                DELETE FROM Offercourt_upload
                WHERE Offer_uploaded_court_id = %s AND Offer_uploader_id = %s
            """
        },
        "Teamup": {
            "query": """
                DELETE FROM Teamup_upload
                WHERE Teamup_court_id = %s AND Teamup_uploader_id = %s
            """
        },
    }
    if table_name not in table_deletes:
        return jsonify({"message": f"Invalid table name: {table_name}"}), 400
    query = table_deletes[table_name]["query"]
    conn = get_pg_conn()
    cur = conn.cursor()
    try:
        cur.execute(query, (court_id, puber_id))
        conn.commit()
        if cur.rowcount == 0:
            return (
                jsonify(
                    {
                        "status": "failure",
                        "message": "No matching records found to delete",
                    }
                ),
                404,
            )
        return (
            jsonify({"status": "success", "message": "Record deleted successfully"}),
            200,
        )
    except Exception as e:
        conn.rollback()
        return (
            jsonify(
                {"message": "Error occurred while deleting record", "error": str(e)}
            ),
            500,
        )
    finally:
        cur.close()
        conn.close()


@bp.route("/update_req", methods=["POST"])
def update_status():
    data = request.get_json()
    table_name = data.get("table_name")
    court_id = data.get("court_id")
    owner_id = data.get("owner_id")
    status = data.get("status")

    if not table_name or not court_id or status is None:
        return (
            jsonify(
                {"message": "Missing required fields: table_name, court_id or status"}
            ),
            400,
        )

    if table_name == "Exchangecourt":
        status_mapping = {0: "retrieved", 1: "exchanged"}
    elif table_name == "Offercourt":
        status_mapping = {0: "retrieved", 1: "offered"}
    else:
        status_mapping = {0: "retrieved", 1: "responsed"}
    status_value = status_mapping.get(status)

    if status_value is None:
        return jsonify({"message": "Invalid status value. Must be 0 or 1"}), 400

    table_updates = {
        "Exchangecourt": {
            "query": """
                UPDATE Exchangecourt_record
                SET Exchange_state = %s
                WHERE Exchange_uploader_court_id = %s AND Exchange_uploader_id = %s
            """
        },
        "Offercourt": {
            "query": """
                UPDATE Offercourt_record
                SET Offer_state = %s
                WHERE Offer_uploader_court_id = %s AND Offer_uploader_id = %s
            """
        },
        "Teamup": {
            "query": """
                UPDATE Teamup_request_record
                SET Teamup_request_state = %s
                WHERE Teamup_court_id = %s AND Offer_uploader_id = %s
            """
        },
    }

    if table_name not in table_updates:
        return jsonify({"message": f"Invalid table name: {table_name}"}), 400

    query = table_updates[table_name]["query"]
    conn = get_pg_conn()
    cur = conn.cursor()
    try:
        cur.execute(query, (status_value, court_id, owner_id))
        conn.commit()
        if cur.rowcount == 0:
            return (
                jsonify(
                    {
                        "status": "failure",
                        "message": "No matching records found to update",
                    }
                ),
                404,
            )
        return (
            jsonify(
                {
                    "status": "success",
                    "message": f"Status updated to '{status_value}' successfully",
                }
            ),
            200,
        )
    except Exception as e:
        conn.rollback()
        return (
            jsonify(
                {"message": "Error occurred while deleting record", "error": str(e)}
            ),
            500,
        )
    finally:
        cur.close()
        conn.close()


@bp.route("/get_available_courts", methods=["POST"])
def get_available_courts():
    data = request.get_json()
    my_id = data.get("my_id")
    if not my_id:
        return jsonify({"message": "Missing my_id parameter"}), 400

    conn = get_pg_conn()
    cur = conn.cursor()
    try:
        query = """
            SELECT Court_id
            FROM CourtInfo
            WHERE Court_owner = %s
            AND Court_id NOT IN (
                SELECT Offer_uploaded_court_id FROM Offercourt_upload WHERE Offer_uploaded_court_id IS NOT NULL
            )
            AND Court_id NOT IN (
                SELECT Teamup_court_id FROM Teamup_upload WHERE Teamup_court_id IS NOT NULL
            )
        """
        cur.execute(query, (my_id,))
        result = cur.fetchall()
        court_ids = [row[0] for row in result]
        if court_ids:
            return jsonify({"available_courts": court_ids}), 200
        else:
            return (
                jsonify({"message": "No available courts found for the given owner"}),
                404,
            )
    except Exception as e:
        return (
            jsonify({"message": "Error occurred while fetching data", "error": str(e)}),
            500,
        )
    finally:
        cur.close()
        conn.close()
