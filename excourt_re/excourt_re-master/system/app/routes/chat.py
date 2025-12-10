import os
from datetime import datetime

import psycopg2.extras
from flask import Blueprint, jsonify, request, current_app
from flask_socketio import join_room

from app import get_pg_conn, socketio

bp = Blueprint("chat", __name__, url_prefix="/chat")


# 发送消息
@bp.route("/send", methods=["POST"])
def send_message():
    data = request.get_json()
    sender_id = data.get("Sender_id")
    receiver_id = data.get("Receiver_id")
    message_sent = data.get("Message_sent", "")
    message_type = data.get("Message_type", "text")
    pic_url = data.get("Pic_url", None)
    message_time = datetime.now()

    if not sender_id or not receiver_id:
        return jsonify({"message": "Missing required fields"}), 400

    conn = get_pg_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO ConversationInfo (
                Sender_id, Receiver_id, Message_sent, Message_type, Pic_url, Message_time, Is_read, Is_deleted
            )
            VALUES (%s, %s, %s, %s, %s, %s, 0, 0)
        """,
            (sender_id, receiver_id, message_sent, message_type, pic_url, message_time),
        )
        conn.commit()

        socketio.emit(
            "new_message",
            {
                "Sender_id": sender_id,
                "Receiver_id": receiver_id,
                "Message_sent": message_sent,
                "Message_type": message_type,
                "Pic_url": pic_url,
                "Message_time": message_time.strftime("%Y-%m-%d %H:%M:%S"),
            },
            room=f"user_{receiver_id}",
        )

        return (
            jsonify({"message": "Message sent successfully", "status": "success"}),
            201,
        )
    except Exception as e:
        conn.rollback()
        return (
            jsonify(
                {"message": "Error occurred while sending message", "error": str(e)}
            ),
            500,
        )
    finally:
        cur.close()
        conn.close()


# 发送图片消息
@bp.route("/sendphoto", methods=["POST"])
def send_photo():
    if "photo" not in request.files:
        return jsonify({"message": "No photo part in the request"}), 400

    file = request.files["photo"].stream.read()
    sender_id = request.form.get("Sender_id")
    receiver_id = request.form.get("Receiver_id")
    message_type = "image"
    message_time = datetime.now()

    if not sender_id or not receiver_id:
        return jsonify({"message": "Missing sender_id or receiver_id"}), 400

    if not file:
        return jsonify({"message": "No selected file"}), 400

    conn = get_pg_conn()
    cur = conn.cursor()
    conversation_id = None
    try:
        # Insert record and get Conversation_id
        cur.execute(
            """
            INSERT INTO ConversationInfo (
                Sender_id, Receiver_id, Message_sent, Message_type, Pic_url, Message_time, Is_read, Is_deleted
            )
            VALUES (%s, %s, %s, %s, %s, %s, 0, 0)
            RETURNING Conversation_id
        """,
            (
                sender_id,
                receiver_id,
                "",
                message_type,
                "",
                message_time,
            ),  # Pic_url is initially empty or placeholder
        )
        result = cur.fetchone()
        if result is None:
            raise Exception("Failed to retrieve conversation_id after insert.")
        conversation_id = result[0]

        # Prepare file path and save file
        qr_folder_path = current_app.config.get("QR_FOLDER")
        if not qr_folder_path:
            raise Exception("QR_FOLDER not configured in the application.")

        if not os.path.exists(qr_folder_path):
            os.makedirs(qr_folder_path, exist_ok=True)

        file_name = f"{conversation_id}.jpg"
        file_path = os.path.join(qr_folder_path, file_name)

        with open(file_path, "wb") as f:
            f.write(file)

        # Update Pic_url in the database with the actual file name
        cur.execute(
            """
            UPDATE ConversationInfo
            SET Pic_url = %s
            WHERE Conversation_id = %s
            """,
            (file_name, conversation_id),
        )
        conn.commit()

        # Emit socket event
        socketio.emit(
            "new_message",
            {
                "Sender_id": sender_id,
                "Receiver_id": receiver_id,
                "Message_sent": "",  # Typically empty for images or could be a caption if supported
                "Message_type": message_type,
                "Pic_url": file_name,  # Send the actual filename (or full URL if applicable)
                "Message_time": message_time.strftime("%Y-%m-%d %H:%M:%S"),
                "Conversation_id": conversation_id,
            },
            room=f"user_{receiver_id}",
        )

        return (
            jsonify(
                {
                    "pic_url": file_name,
                    "message": "Message sent successfully",
                    "status": "success",
                    "conversation_id": conversation_id,
                }
            ),
            201,
        )
    except Exception as e:
        conn.rollback()
        # If conversation_id was generated but file saving/DB update failed,
        # consider if the initial DB record should be deleted or marked as failed.
        # For simplicity, current error handling just rolls back.
        return (
            jsonify({"message": "Error occurred while sending photo", "error": str(e)}),
            500,
        )
    finally:
        cur.close()
        conn.close()


# 聊天历史
@bp.route("/history", methods=["POST"])
def get_chat_history():
    data = request.get_json()
    user_id = data.get("user_id")
    contact_id = data.get("contact_id")
    page = int(data.get("page", 1))
    limit = int(data.get("limit", 20))
    offset = (page - 1) * limit

    if not user_id or not contact_id:
        return jsonify({"message": "Missing required fields"}), 400

    conn = get_pg_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cur.execute(
            """
            SELECT *
            FROM ConversationInfo
            WHERE (Sender_id = %s AND Receiver_id = %s)
               OR (Sender_id = %s AND Receiver_id = %s)
            ORDER BY Message_time
            LIMIT %s OFFSET %s
            """,
            (user_id, contact_id, contact_id, user_id, limit, offset),
        )
        messages = cur.fetchall()
        return (
            jsonify(
                {
                    "status": "success",
                    "message": "Chat history fetched successfully",
                    "data": [dict(row) for row in messages],
                }
            ),
            200,
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "message": "Error occurred while fetching chat history",
                    "error": str(e),
                }
            ),
            500,
        )
    finally:
        cur.close()
        conn.close()


# 标记为已读
@bp.route("/mark_as_read", methods=["POST"])
def mark_as_read():
    data = request.get_json()
    user_id = data.get("user_id")
    contact_id = data.get("contact_id")

    if not user_id or not contact_id:
        return jsonify({"message": "Missing required fields"}), 400

    conn = get_pg_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            UPDATE ConversationInfo
            SET Is_read = 1
            WHERE Sender_id = %s AND Receiver_id = %s AND Is_read = 0
        """,
            (contact_id, user_id),
        )
        conn.commit()
        return jsonify({"message": "Messages marked as read successfully"}), 200
    except Exception as e:
        conn.rollback()
        return (
            jsonify(
                {
                    "message": "Error occurred while marking messages as read",
                    "error": str(e),
                }
            ),
            500,
        )
    finally:
        cur.close()
        conn.close()


# 获取未读消息数量
@bp.route("/unread_count", methods=["GET"])
def get_unread_count():
    data = request.get_json()
    user_id = data.get("student_id")
    if not user_id:
        return jsonify({"message": "Missing required fields"}), 400

    conn = get_pg_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cur.execute(
            """
            SELECT Sender_id, COUNT(*) as unread_count
            FROM ConversationInfo
            WHERE Receiver_id = %s AND Is_read = 0
            GROUP BY Sender_id
        """,
            (user_id,),
        )
        unread_counts = cur.fetchall()
        return jsonify([dict(row) for row in unread_counts]), 200
    except Exception as e:
        return (
            jsonify(
                {
                    "message": "Error occurred while fetching unread counts",
                    "error": str(e),
                }
            ),
            500,
        )
    finally:
        cur.close()
        conn.close()


# 获取所有有过聊天记录的学生信息
@bp.route("/contacts", methods=["POST"])
def get_chat_contacts():
    data = request.get_json()
    student_id = data.get("student_id")

    if not student_id:
        return jsonify({"message": "缺少必要的参数: student_id"}), 400

    conn = get_pg_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
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
        cur.execute(sql_query_contacts, (student_id, student_id))
        contacts = cur.fetchall()
        contact_list = [
            {
                "student_id": row[0],
                "name": row[1],
                "nickname": row[2],
                "profile_url": row[3],
            }
            for row in contacts
        ]
        return (
            jsonify(
                {
                    "status": "success",
                    "message": "获取聊天联系人成功",
                    "data": contact_list,
                }
            ),
            200,
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "message": "Error occurred while fetching chat contacts",
                    "error": str(e),
                }
            ),
            500,
        )
    finally:
        cur.close()
        conn.close()


# WebSocket 事件
@socketio.on("connect")
def handle_connect():
    print("A user connected.")


@socketio.on("join")
def handle_join(data):
    user_id = data.get("user_id")
    if user_id:
        room = f"user_{user_id}"
        join_room(room)
        print(f"User {user_id} joined room {room}")
