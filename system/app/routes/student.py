from flask import Blueprint, request, jsonify
from app import mysql
from datetime import datetime
bp = Blueprint('student', __name__, url_prefix='/student')

@bp.route('/register', methods=['POST'])
def register_student():
    data = request.get_json()

    # 从请求中获取数据
    student_id = data.get('Student_id')
    student_name = data.get('Student_name')
    student_nickname = data.get('Student_nickname')
    student_phone = data.get('Student_phone')
    student_password = data.get('Student_password')

    # 校验必要字段
    if not student_id or not student_name or not student_password or not student_nickname:
        return jsonify({'message': 'Missing required fields'}), 400

    cur = mysql.connection.cursor()
    try:
        cur.execute("""
            INSERT INTO Student (
                Student_id, Student_name, Student_nickname, Student_phone,
                Student_password, Student_credit, Student_level, Student_status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (student_id, student_name, student_nickname, student_phone,
              student_password, 100, 1, 1))
        mysql.connection.commit()
        return jsonify({'message': 'Student registered successfully'}), 201
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'message': 'Error occurred while registering student', 'error': str(e)}), 500

# 学生登录
@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    student_id = data.get('Student_id')
    password = data.get('Student_password')

    # 检查是否提供必要参数
    if not student_id or not password:
        return jsonify({'message': 'Student_id and password are required'}), 400

    cur = mysql.connection.cursor()

    # 检查学号是否存在
    cur.execute("SELECT Student_password FROM Student WHERE Student_id = %s", (student_id,))
    result = cur.fetchone()

    if not result:
        # 学号不存在
        return jsonify({'message': 'Student_id not found'}), 404

    # 验证密码
    if result[0] != password:
        # 密码错误
        return jsonify({'message': 'Incorrect password'}), 401

    # 登录成功
    cur.execute("SELECT Student_id, Student_name FROM Student WHERE Student_id = %s", (student_id,))
    student = cur.fetchone()
    return jsonify({'message': 'Login successful', 'Student_id': student[0], 'Student_name': student[1]})

# 修改个人信息接口
@bp.route('/update', methods=['POST'])
def update_info():
    data = request.get_json()
    search_id = data.get('search_id')
    profileurl = data.get('profileurl')
    nickname = data.get('nickname')
    phone = data.get('phone')
    level = data.get('level')

    if not search_id or not profileurl or not nickname or not phone or not level:
        return jsonify({"status": "error", "message": "缺少必要的参数"}), 400

    try:
        with mysql.connection.cursor() as cursor:
            # 查询用户的详细信息
            sql_update_student = """
                UPDATE Student
                SET Student_profileurl = %s, Student_nickname = %s, Student_phone = %s, Student_level = %s
                WHERE Student_id = %s
            """
            cursor.execute(sql_update_student, (profileurl, nickname, phone, level ,search_id))

            # 如果没有找到用户，返回错误信息
            mysql.connection.commit()

        return jsonify({"status": "success", "message": "用户信息已更新"}), 200


    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@bp.route('/owned-courts', methods=['POST'])
def get_owned_courts():
    data = request.get_json()

    # 从请求体中获取 student_id
    student_id = data.get('student_id')

    # 校验 student_id 是否存在
    if not student_id:
        return jsonify({"message": "Missing required field: student_id"}), 400

    cur = mysql.connection.cursor()

    try:
        # 查询学生拥有的场地号
        query = """
            SELECT Court_id, Court_no, Court_campus, Court_date, Court_time, Court_owner
            FROM CourtInfo
            WHERE Court_owner = %s AND Court_state = 'owned'
        """
        cur.execute(query, (student_id,))
        results = cur.fetchall()

        # 获取今天的日期
        today = datetime.today().date()

        # 格式化返回数据
        owned_courts = [
            {
                "dayId": (row[3] - today).days,  # 计算相对于今天的天数差
                "Court_owner": row[5],
                "Court_no": row[1],
                "Court_time": row[4],
                "Court_id" : row[0]
            }
            for row in results
        ]

        return jsonify({"student_id": student_id, "owned_courts": owned_courts}), 200

    except Exception as e:
        return jsonify({"message": "Error occurred while fetching owned courts", "error": str(e)}), 500


@bp.route('/get_operation_records', methods=['GET'])
def get_operation_records():
    data = request.get_json()
    operator_id = data.get('student_id')

    # 校验必要字段
    if not operator_id:
        return jsonify({'message': 'Missing required fields'}), 400

    cur = mysql.connection.cursor()
    try:
        # 查询操作记录
        query = """
            SELECT Operation_record_id, Operation_type, Operation_id, Operation_status, Operation_time
            FROM Operation_record
            WHERE Operator_id = %s
            ORDER BY Operation_time DESC
        """
        cur.execute(query, (operator_id,))
        operation_records = cur.fetchall()

        # 将查询结果转换为字典列表
        operation_records_list = [{
            'operation_record_id': row[0],
            'operation_type': row[1],
            'operation_id': row[2],
            'operation_status': row[3],
            'operation_time': row[4].strftime('%Y-%m-%d %H:%M:%S')  # 格式化时间
        } for row in operation_records]

        return jsonify(operation_records_list), 200

    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'message': 'Error occurred while fetching operation records', 'error': str(e)}), 500
    finally:
        cur.close()

# 查询好友接口
@bp.route('/find', methods=['POST'])
def query_friend():
    search_id = request.json.get('search_id')

    if not search_id:
        return jsonify({"status": "error", "message": "缺少必要的参数"}), 400

    try:
        with mysql.connection.cursor() as cursor:
            # 查询用户的详细信息
            sql_query_student = """
                SELECT Student_id, Student_name, Student_profileurl, Student_nickname, Student_credit, Student_level, Student_status
                ,Student_phone
                FROM Student
                WHERE Student_id = %s
            """
            cursor.execute(sql_query_student, (search_id,))
            user_info = cursor.fetchone()

            # 如果没有找到用户，返回错误信息
            if not user_info:
                return jsonify({"status": "error", "message": "用户不存在"}), 404

    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

    return jsonify({"status": "success", "message": "获取用户信息成功", "data": user_info}), 200

#查询其他人发布的换场信息----courts-view用
@bp.route('/get_exchangecourt', methods=['POST'])
def get_exchangecourt():
    # 从请求获取 my_id 参数
    data = request.get_json()
    my_id = data.get('my_id')
    # 校验必要字段
    if not my_id:
        return jsonify({'message': 'Missing required fields: my_id'}), 400
    cur = mysql.connection.cursor()
    try:
        # 查询 Exchangecourt_upload 表，排除指定 my_id 的记录
        query = """
            SELECT Exchange_uploaded_court_id AS court_id
            FROM Exchangecourt_upload
            WHERE Exchange_uploader_id != %s
        """
        cur.execute(query, (my_id,))
        court_ids = cur.fetchall()
        # 将查询结果转换为字典列表
        court_ids_list = [{
            'court_id': row[0]
        } for row in court_ids]
        return jsonify({'court_ids_list':court_ids_list}), 200
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'message': 'Error occurred while fetching court ids', 'error': str(e)}), 500
    finally:
        cur.close()
        
# 要检查有几个人相应，满没满
@bp.route('/get_teamupcourt', methods=['POST'])
def get_teamupcourt():
    # 从请求获取 my_id 参数
    data = request.get_json()
    my_id = data.get('my_id')
    # 校验必要字段
    if not my_id:
        return jsonify({'message': 'Missing required fields: my_id'}), 400
    cur = mysql.connection.cursor()
    try:
        # 查询 Exchangecourt_upload 表，排除指定 my_id 的记录
        query = """
            SELECT Teamup_court_id AS court_id
            FROM Teamup_upload
            WHERE Teamup_uploader_id != %s
        """
        cur.execute(query, (my_id,))
        court_ids = cur.fetchall()
        # 将查询结果转换为字典列表
        court_ids_list = [{
            'court_id': row[0]
        } for row in court_ids]
        return jsonify({'court_ids_list':court_ids_list}), 200
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'message': 'Error occurred while fetching court ids', 'error': str(e)}), 500
    finally:
        cur.close()
        
@bp.route('/get_offercourt', methods=['POST'])
def get_offercourt():
    # 从请求获取 my_id 参数
    data = request.get_json()
    my_id = data.get('my_id')
    # 校验必要字段
    if not my_id:
        return jsonify({'message': 'Missing required fields: my_id'}), 400
    cur = mysql.connection.cursor()
    try:
        # 查询 Exchangecourt_upload 表，排除指定 my_id 的记录
        query = """
            SELECT Offer_uploaded_court_id AS court_id
            FROM Offercourt_upload
            WHERE Offer_uploader_id != %s AND (offer_upload_state = 'not_responsed' or offer_upload_state = 'responsed')
        """
        cur.execute(query, (my_id,))
        court_ids = cur.fetchall()
        # 将查询结果转换为字典列表
        court_ids_list = [{
            'court_id': row[0]
        } for row in court_ids]
        return jsonify({'court_ids_list':court_ids_list}), 200
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'message': 'Error occurred while fetching court ids', 'error': str(e)}), 500
    finally:
        cur.close()
        

        
# 获取upload表中我作为发布者的记录,放在我的发布
@bp.route('/get_apply', methods=['POST'])
def get_user_apply():
    data = request.get_json()
    my_id = data.get('my_id')
    if not my_id:
        return jsonify({'message': 'Missing required fields: my_id'}), 400

    cur = mysql.connection.cursor()
    try:
        # 查询 Exchangecourt_upload 表
        query1 = """
            SELECT Exchange_uploaded_court_id AS court_id, Exchange_upload_state AS status, 'Exchangecourt' AS source
            FROM Exchangecourt_upload
            WHERE Exchange_uploader_id = %s
        """
        cur.execute(query1, (my_id,))
        exchangecourt_data = cur.fetchall()
        print("Exchangecourt Data:", exchangecourt_data)  # 调试信息

        # 查询 Offercourt_upload 表
        query2 = """
            SELECT Offer_uploaded_court_id AS court_id, Offer_upload_state AS status, 'Offercourt' AS source
            FROM Offercourt_upload
            WHERE Offer_uploader_id = %s
        """
        cur.execute(query2, (my_id,))
        offercourt_data = cur.fetchall()
        print("Offercourt Data:", offercourt_data)  # 调试信息

        # 查询 Teamup_upload 表
        query3 = """
            SELECT Teamup_court_id AS court_id, Teamup_upload_state AS status, 'Teamup' AS source
            FROM Teamup_upload
            WHERE Teamup_uploader_id = %s
        """
        cur.execute(query3, (my_id,))
        teamup_data = cur.fetchall()
        print("Teamup Data:", teamup_data)  # 调试信息

        # 整合数据
        result = [
            {"court_id": row[0], "status": row[1], "source": row[2]}
            for row in exchangecourt_data + offercourt_data + teamup_data
        ]
        print("Combined Result:", result)  # 调试信息

        return jsonify({"status": "success", "data": result}), 200

    except Exception as e:
        mysql.connection.rollback()
        print("Error:", e)  # 打印具体错误
        return jsonify({"message": "Error occurred while fetching court ids", "error": str(e)}), 500

    finally:
        cur.close()




# 获取record表中我作为响应者的记录,放在我的申请
@bp.route('/get_my_request', methods=['POST'])
def get_user_repond():
    # 从请求获取 my_id 参数
    data = request.get_json()
    my_id = data.get('my_id')
    # 校验必要字段
    if not my_id:
        return jsonify({'message': 'Missing required fields: my_id'}), 400
    cur = mysql.connection.cursor()
    try:
        # 查询 Exchangecourt_upload 表
        query = """
            SELECT Exchange_responser_court_id AS court_id,Exchange_state AS status, 'Exchangecourt' AS source
            FROM Exchangecourt_record
            WHERE Exchange_responser_id = %s
        """
        cur.execute(query, (my_id,))
        exchangecourt_data = cur.fetchall()
        # 查询 Offercourt_upload 表
        query = """
            SELECT Offer_uploader_court_id AS court_id,Offer_state AS status, 'Offercourt' AS source
            FROM Offercourt_record
            WHERE Offer_responser_id = %s
        """
        cur.execute(query, (my_id,))
        offercourt_data = cur.fetchall()
        # 查询 Teamup_upload 表
        query = """
            SELECT Teamup_court_id AS court_id,Teamup_request_state AS status, 'Teamup' AS source
            FROM Teamup_request_record
            WHERE Teamup_requester_id = %s
        """
        cur.execute(query, (my_id,))
        teamup_data = cur.fetchall()
        # 整合所有数据
        result = [
            {"court_id": row[0],"status":row[1], "source": row[2]}
            for row in exchangecourt_data + offercourt_data + teamup_data
        ]
        return jsonify({"status": "success", "data": result}), 200
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"message": "Error occurred while fetching court ids", "error": str(e)}), 500
    finally:
        cur.close()



                
@bp.route('/delete_apply', methods=['POST'])
def delete_apply():
    # 从请求获取表名、court_id 和 uploader_id
    data = request.get_json()
    table_name = data.get('table_name')  # 例如 'Exchangecourt', 'Offercourt', 'Teamup'
    court_id = data.get('court_id')
    applier_id = data.get('applier_id')

    # 校验必要字段
    if not table_name or not court_id or not applier_id:
        return jsonify({'message': 'Missing required fields: table_name, court_id or uploader_id'}), 400

    # 定义每个表的删除模板
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

    # 检查表名是否有效
    if table_name not in table_deletes:
        return jsonify({'message': f'Invalid table name: {table_name}'}), 400

    query = table_deletes[table_name]["query"]

    cur = mysql.connection.cursor()
    try:
        # 执行删除操作
        cur.execute(query, (court_id, applier_id))
        mysql.connection.commit()

        # 检查受影响的行数
        if cur.rowcount == 0:
            return jsonify({"status": "failure", "message": "No matching records found to delete"}), 404

        return jsonify({"status": "success", "message": "Record deleted successfully"}), 200
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"message": "Error occurred while deleting record", "error": str(e)}), 500
    finally:
        cur.close()
        

@bp.route('/delete_pub', methods=['POST'])
def delete_pub():
    # 从请求获取表名、court_id 和 uploader_id
    data = request.get_json()
    table_name = data.get('table_name')  # 例如 'Exchangecourt', 'Offercourt', 'Teamup'
    court_id = data.get('court_id')
    puber_id = data.get('puber_id')
    # 校验必要字段
    if not table_name or not court_id or not puber_id:
        return jsonify({'message': 'Missing required fields: table_name, court_id or uploader_id'}), 400
    # 定义每个表的删除模板
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
    # 检查表名是否有效
    if table_name not in table_deletes:
        return jsonify({'message': f'Invalid table name: {table_name}'}), 400
    query = table_deletes[table_name]["query"]
    cur = mysql.connection.cursor()
    try:
        # 执行删除操作
        cur.execute(query, (court_id, puber_id))
        mysql.connection.commit()
        # 检查受影响的行数
        if cur.rowcount == 0:
            return jsonify({"status": "failure", "message": "No matching records found to delete"}), 404
        return jsonify({"status": "success", "message": "Record deleted successfully"}), 200
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"message": "Error occurred while deleting record", "error": str(e)}), 500
    finally:
        cur.close()
        

@bp.route('/update_req', methods=['POST'])
def update_status():
    # 从请求获取表名、court_id 和 status
    data = request.get_json()
    table_name = data.get('table_name')  # 例如 'Exchangecourt', 'Offercourt', 'Teamup'
    court_id = data.get('court_id')
    owner_id = data.get('owner_id')
    status = data.get('status')  # 0 或 1 0retrieved, 1 approval

    # 校验必要字段
    if not table_name or not court_id or status is None:
        return jsonify({'message': 'Missing required fields: table_name, court_id or status'}), 400

    # 将 status 转换为对应的字符串值
    if table_name=='Exchangecourt':
        status_mapping = {0: 'retrieved', 1: 'exchanged'}
    elif table_name=='Offercourt':
        status_mapping = {0: 'retrieved', 1: 'offered'}
    else:
        status_mapping = {0: 'retrieved', 1: 'responsed'}
    status_value = status_mapping.get(status)

    if status_value is None:
        return jsonify({'message': 'Invalid status value. Must be 0 or 1'}), 400

    # 定义每个表的更新模板
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

    # 检查表名是否有效
    if table_name not in table_updates:
        return jsonify({'message': f'Invalid table name: {table_name}'}), 400

    query = table_updates[table_name]["query"]

    cur = mysql.connection.cursor()
    try:
        # 执行更新操作
        cur.execute(query, (status_value, court_id, owner_id))
        mysql.connection.commit()

        # 检查受影响的行数
        if cur.rowcount == 0:
            return jsonify({"status": "failure", "message": "No matching records found to update"}), 404

        return jsonify({"status": "success", "message": f"Status updated to '{status_value}' successfully"}), 200
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"message": "Error occurred while deleting record", "error": str(e)}), 500
    finally:
        cur.close()
        

# 获取当前用户可以交换的场地
@bp.route('/get_available_courts', methods=['POST'])
def get_available_courts():
    # 获取前端传来的 my_id
    data = request.get_json()
    my_id = data.get('my_id')
    if not my_id:
        return jsonify({'message': 'Missing my_id parameter'}), 400
    try:
        cur = mysql.connection.cursor()
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
            return jsonify({'available_courts': court_ids}), 200
        else:
            return jsonify({'message': 'No available courts found for the given owner'}), 404
    except Exception as e:
        return jsonify({'message': 'Error occurred while fetching data', 'error': str(e)}), 500
    finally:
        cur.close()