from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

mysql = MySQL(app)


# 获取所有学生信息
@app.route('/students', methods=['GET'])
def get_students():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Student")
    students = cur.fetchall()
    result = []
    for student in students:
        result.append({
            'Student_id': student[0],
            'Student_name': student[1],
            'Student_phone': student[2]
        })
    return jsonify(result)


# 添加新学生
@app.route('/students', methods=['POST'])
def add_student():
    data = request.get_json()
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO Student (Student_id, Student_name, Student_phone, Student_password) VALUES (%s, %s, %s, %s)", 
                (data['Student_id'], data['Student_name'], data['Student_phone'], data['Student_password']))
    mysql.connection.commit()
    return jsonify({'message': 'Student added successfully'})

# 获取某个场地信息
@app.route('/courts/<court_id>', methods=['GET'])
def get_court(court_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM CourtInfo WHERE Court_id = %s", (court_id,))
    court = cur.fetchone()
    if court:
        return jsonify({
            'Court_id': court[0],
            'Court_campus': court[1],
            'Court_date': court[2].isoformat(),
            'Court_time': court[3],
            'Court_no': court[4],
            'Court_state': court[5],
            'Court_owner': court[6],
            'Court_qrcodeurl': court[7]
        })
    else:
        return jsonify({'message': 'Court not found'}), 404
    

# 验证学生信息是否存在，用于注册
@app.route('/verify', methods=['POST'])
def verify_student():
    data = request.get_json()
    student_id = data.get('Student_id')
    student_name = data.get('Student_name')
    student_password = data.get('Student_password')

    # 检查是否提供必要参数
    if not student_id or not student_name or not student_password:
        return jsonify({'message': 'Missing required parameters'}), 400

    cur = mysql.connection.cursor()

    # 查询是否有匹配的记录
    query = """
        SELECT * FROM Student
        WHERE Student_id = %s AND Student_name = %s AND Student_password = %s
    """
    cur.execute(query, (student_id, student_name, student_password))
    result = cur.fetchone()

    if result:
        # 匹配成功
        return jsonify({'message': 'Record found', 'status': 'success'}), 200
    else:
        # 匹配失败
        return jsonify({'message': 'No matching record found', 'status': 'failure'}), 404


# 运行Flask应用
if __name__ == '__main__':
    app.run(host = '0.0.0.0', debug=True)
