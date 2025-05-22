from flask import Blueprint, request, jsonify
from app import mysql

bp = Blueprint('lost_and_found', __name__, url_prefix='/lost_and_found')

#用户发布一条自己丢失的物品
@bp.route('/lost/create', methods=['POST'])
def create_lost_item():
    data = request.get_json()

    # 从请求中获取数据
    lost_uploader_id = data.get('Lost_uploader_id')
    lost_item_name = data.get('Lost_item_name')
    lost_description = data.get('Lost_description')
    lost_position = data.get('Lost_position')
    lost_time = data.get('Lost_time')  # 时间需要是标准格式
    lost_contact = data.get('Lost_contact')
    lost_item_pic_url = data.get('Lost_item_pic_url')

    # 校验必要字段
    if not lost_uploader_id or not lost_item_name or not lost_description or not lost_position or not lost_time:
        return jsonify({'message': 'Missing required fields'}), 400

    cur = mysql.connection.cursor()

    try:
        # 插入到 MyLost 表
        insert_query = """
            INSERT INTO MyLost (
                Lost_uploader_id, Lost_item_name, Lost_description,
                Lost_position, Lost_time, Lost_contact, Lost_item_pic_url
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cur.execute(insert_query, (
            lost_uploader_id, lost_item_name, lost_description,
            lost_position, lost_time, lost_contact, lost_item_pic_url
        ))

        # 提交事务
        mysql.connection.commit()
        return jsonify({'message': 'Lost item record created successfully'}), 201

    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'message': 'Error occurred while creating lost item record', 'error': str(e)}), 500

@bp.route('/lost/getall', methods=['POST'])
def get_lost_items():
    cur = mysql.connection.cursor()

    try:
        # 查询所有失物记录
        query = "SELECT * FROM MyLost"
        cur.execute(query)
        results = cur.fetchall()

        # 格式化返回数据
        lost_items = [
            {
                "Lost_id": row[0],
                "Lost_uploader_id": row[1],
                "Lost_item_name": row[2],
                "Lost_description": row[3],
                "Lost_position": row[4],
                "Lost_time": row[5].strftime('%Y-%m-%d %H:%M:%S'),
                "Lost_contact": row[6],
                "Lost_item_pic_url": row[7]
            }
            for row in results
        ]

        return jsonify({"lost_items": lost_items}), 200

    except Exception as e:
        return jsonify({"message": "Error occurred while fetching lost items", "error": str(e)}), 500

#用户找到一个丢失的物品
@bp.route('/found/create', methods=['POST'])
def create_found_item():
    data = request.get_json()

    # 从请求中获取数据
    found_uploader_id = data.get('Found_uploader_id')
    found_item_name = data.get('Found_item_name')
    found_description = data.get('Found_description')
    found_position = data.get('Found_position')
    found_time = data.get('Found_time')  # 时间需要是标准格式
    found_contact = data.get('Found_contact')
    found_item_pic_url = data.get('Found_item_pic_url')

    # 校验必要字段
    if not found_uploader_id or not found_item_name or not found_description or not found_position or not found_time:
        return jsonify({'message': 'Missing required fields'}), 400

    cur = mysql.connection.cursor()

    try:
        # 插入到 MyFound 表
        insert_query = """
            INSERT INTO MyFound (
                Found_uploader_id, Found_item_name, Found_description,
                Found_position, Found_time, Found_contact, Found_item_pic_url
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cur.execute(insert_query, (
            found_uploader_id, found_item_name, found_description,
            found_position, found_time, found_contact, found_item_pic_url
        ))

        # 提交事务
        mysql.connection.commit()
        return jsonify({'message': 'Found item record created successfully'}), 201

    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'message': 'Error occurred while creating found item record', 'error': str(e)}), 500
    
@bp.route('/found/getall', methods=['GET'])
def get_found_items():
    cur = mysql.connection.cursor()

    try:
        # 查询所有招领记录
        query = "SELECT * FROM MyFound"
        cur.execute(query)
        results = cur.fetchall()

        # 格式化返回数据
        found_items = [
            {
                "Found_id": row[0],
                "Found_uploader_id": row[1],
                "Found_item_name": row[2],
                "Found_description": row[3],
                "Found_position": row[4],
                "Found_time": row[5].strftime('%Y-%m-%d %H:%M:%S'),
                "Found_contact": row[6],
                "Found_item_pic_url": row[7]
            }
            for row in results
        ]

        return jsonify({"found_items": found_items}), 200

    except Exception as e:
        return jsonify({"message": "Error occurred while fetching found items", "error": str(e)}), 500

