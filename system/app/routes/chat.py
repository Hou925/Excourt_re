from flask import Blueprint, request, jsonify
from app import mysql, socketio
from flask_socketio import emit, join_room
from datetime import datetime
from MySQLdb.cursors import DictCursor

bp = Blueprint('chat', __name__, url_prefix='/chat')

# 发送消息
@bp.route('/send', methods=['POST'])
def send_message():
    data = request.get_json()

    # 获取发送者和接收者信息
    sender_id = data.get('Sender_id')
    receiver_id = data.get('Receiver_id')
    message_sent = data.get('Message_sent', '')
    message_type = data.get('Message_type', 'text')
    pic_url = data.get('Pic_url', None)
    message_time = datetime.now()

    if not sender_id or not receiver_id:
        return jsonify({'message': 'Missing required fields'}), 400

    try:
        with mysql.connection.cursor() as cursor:
            # 插入消息记录
            cursor.execute("""
                INSERT INTO ConversationInfo (
                    Sender_id, Receiver_id, Message_sent, Message_type, Pic_url, Message_time, Is_read, Is_deleted
                )
                VALUES (%s, %s, %s, %s, %s, %s, 0, 0)
            """, (sender_id, receiver_id, message_sent, message_type, pic_url, message_time))
            mysql.connection.commit()

            # 实时通知接收者
            socketio.emit('new_message', {
                "Sender_id": sender_id,
                "Receiver_id": receiver_id,
                "Message_sent": message_sent,
                "Message_type": message_type,
                "Pic_url": pic_url,
                "Message_time": message_time.strftime('%Y-%m-%d %H:%M:%S')
            }, room=f"user_{receiver_id}")

        return jsonify({'message': 'Message sent successfully',"status":'success'}), 201
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'message': 'Error occurred while sending message', 'error': str(e)}), 500

import os
QR_path = 'QR'
QR_folder = os.path.join(os.getcwd(), QR_path)

# 发送消息
@bp.route('/sendphoto', methods=['POST'])
def send_photo():

    file = request.files['photo'].stream.read()
    # 获取发送者和接收者信息
    sender_id = request.form['Sender_id']
    receiver_id = request.form['Receiver_id']
    message_sent = ''
    message_type = 'image'
    message_time = datetime.now()

    if not sender_id or not receiver_id:
        return jsonify({'message': 'Missing required fields'}), 400

    try:
        with mysql.connection.cursor() as cursor:
            # 插入消息记录
            cursor.execute("""
                INSERT INTO ConversationInfo (
                    Sender_id, Receiver_id, Message_sent, Message_type, Pic_url, Message_time, Is_read, Is_deleted
                )
                VALUES (%s, %s, %s, %s, %s, %s, 0, 0)
            """, (sender_id, receiver_id, message_sent, message_type, '', message_time))
            mysql.connection.commit()

            cursor.execute("""SELECT * FROM ConversationInfo WHERE 
    (Sender_id = %s AND Receiver_id = %s)
    OR (Sender_id = %s AND Receiver_id = %s) ORDER BY Message_time DESC LIMIT 1
            """,(sender_id,receiver_id,receiver_id,sender_id))

            message = cursor.fetchone()
            Conversation_id = message[0]
            file_path = os.path.join(QR_folder, f"{Conversation_id}.jpg")
            with open(file_path, 'wb') as f:
                f.write(file)

        return jsonify({'profileurl': file_path,'message': 'Message sent successfully',"status":'success'}), 201
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'message': 'Error occurred while sending message', 'error': str(e)}), 500

@bp.route('/history', methods=['POST'])
def get_chat_history():
    data = request.get_json()
    user_id = data.get('user_id')
    contact_id = data.get('contact_id')
    page = int(data.get('page', 1))
    limit = int(data.get('limit', 20))
    offset = (page - 1) * limit

    if not user_id or not contact_id:
        return jsonify({'message': 'Missing required fields'}), 400

    try:
        with mysql.connection.cursor(DictCursor) as cursor:
            # 获取聊天记录
            cursor.execute("""
                SELECT * FROM ConversationInfo
                WHERE 
                    (Sender_id = %s AND Receiver_id = %s) OR 
                    (Sender_id = %s AND Receiver_id = %s)
                ORDER BY Message_time ASC
                LIMIT %s OFFSET %s
            """, (user_id, contact_id, contact_id, user_id, limit, offset))
            messages = cursor.fetchall()

        return jsonify({
            "status": "success",
            "message": "Chat history fetched successfully",
            "data": messages
        }), 200
    except Exception as e:
        return jsonify({'message': 'Error occurred while fetching chat history', 'error': str(e)}), 500


# 标记消息为已读
@bp.route('/mark_as_read', methods=['POST'])
def mark_as_read():
    data = request.get_json()

    user_id = data.get('user_id')
    contact_id = data.get('contact_id')

    if not user_id or not contact_id:
        return jsonify({'message': 'Missing required fields'}), 400

    try:
        with mysql.connection.cursor() as cursor:
            # 更新未读消息为已读
            cursor.execute("""
                UPDATE ConversationInfo
                SET Is_read = 1
                WHERE Sender_id = %s AND Receiver_id = %s AND Is_read = 0
            """, (contact_id, user_id))
            mysql.connection.commit()

        return jsonify({'message': 'Messages marked as read successfully'}), 200
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'message': 'Error occurred while marking messages as read', 'error': str(e)}), 500

# 获取未读消息数量
@bp.route('/unread_count', methods=['GET'])
def get_unread_count():
    data = request.get_json()
    user_id = data.get('student_id')

    if not user_id:
        return jsonify({'message': 'Missing required fields'}), 400

    try:
        with mysql.connection.cursor(DictCursor) as cursor:
            # 查询未读消息数量
            cursor.execute("""
                SELECT Sender_id, COUNT(*) as unread_count
                FROM ConversationInfo
                WHERE Receiver_id = %s AND Is_read = 0
                GROUP BY Sender_id
            """, (user_id,))
            unread_counts = cursor.fetchall()

        return jsonify(unread_counts), 200
    except Exception as e:
        return jsonify({'message': 'Error occurred while fetching unread counts', 'error': str(e)}), 500
    
# 获取所有有过聊天记录的学生信息
@bp.route('/contacts', methods=['POST'])
def get_chat_contacts():
    data = request.get_json()
    student_id = data.get('student_id')

    if not student_id:
        return jsonify({'message': '缺少必要的参数: student_id'}), 400

    try:
        with mysql.connection.cursor(DictCursor) as cursor:
            # 查询与当前学生有聊天记录的所有学生的基本信息
            sql_query_contacts = """
                SELECT DISTINCT 
                    s.Student_id, 
                    s.Student_name, 
                    s.Student_nickname, 
                    s.Student_profileurl
                FROM 
                    ConversationInfo c
                JOIN 
                    Student s 
                ON 
                    (c.Sender_id = s.Student_id AND c.Receiver_id = %s) 
                    OR (c.Receiver_id = s.Student_id AND c.Sender_id = %s)
            """
            cursor.execute(sql_query_contacts, (student_id, student_id))
            contacts = cursor.fetchall()

        # 格式化结果
        contact_list = [
            {
                "student_id": contact["Student_id"],
                "name": contact["Student_name"],
                "nickname": contact["Student_nickname"],
                "profile_url": contact["Student_profileurl"]
            }
            for contact in contacts
        ]

        return jsonify({
            "status": "success",
            "message": "获取聊天联系人成功",
            "data": contact_list
        }), 200
    except Exception as e:
        return jsonify({'message': 'Error occurred while fetching chat contacts', 'error': str(e)}), 500


# WebSocket 事件
@socketio.on('connect')
def handle_connect():
    print("A user connected.")

@socketio.on('join')
def handle_join(data):
    user_id = data.get('user_id')
    if user_id:
        room = f"user_{user_id}"
        join_room(room)
        print(f"User {user_id} joined room {room}")
