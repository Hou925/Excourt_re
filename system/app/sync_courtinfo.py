import mysql.connector
import time
import traceback

# 配置学校和本地数据库连接
school_db_config = {
    'host': '123.60.86.239',
    'port': 3306,
    'user': 'root',
    'password': 'QWer1234',
    'database': 'school'
}

local_db_config = {
    'host': '123.60.86.239',
    'port': 3306,
    'user': 'root',
    'password': 'QWer1234',
    'database': 'system'
}

def sync_court_info():
    while True:
        try:
            # 连接到学校数据库和本地数据库
            school_db = mysql.connector.connect(**school_db_config)
            local_db = mysql.connector.connect(**local_db_config)

            school_cursor = school_db.cursor(dictionary=True)
            local_cursor = local_db.cursor(dictionary=True)

            # 查询学校数据库的 CourtInfo 表
            school_cursor.execute("SELECT * FROM CourtInfo")
            school_data = school_cursor.fetchall()

            # 查询本地数据库的 CourtInfo 表
            local_cursor.execute("SELECT * FROM CourtInfo")
            local_data = local_cursor.fetchall()

            # 构建映射
            school_mapping = {row['Court_id']: row for row in school_data}
            local_mapping = {row['Court_id']: row for row in local_data}

            # 同步新增和更新的数据
            for court_id, school_row in school_mapping.items():
                if court_id in local_mapping:
                    # 更新记录
                    local_row = local_mapping[court_id]
                    if (school_row['Court_state'] != local_row['Court_state'] or
                            school_row['Court_owner'] != local_row['Court_owner']):
                        local_cursor.execute("""
                            UPDATE CourtInfo
                            SET Court_state = %s, Court_owner = %s
                            WHERE Court_id = %s
                        """, (school_row['Court_state'], school_row['Court_owner'], court_id))
                else:
                    # 插入新记录
                    local_cursor.execute("""
                        INSERT INTO CourtInfo (Court_id, Court_campus, Court_date, Court_time, Court_no, Court_state, Court_owner, Court_qrcodeurl)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (school_row['Court_id'], school_row['Court_campus'], school_row['Court_date'],
                        school_row['Court_time'], school_row['Court_no'], school_row['Court_state'],
                        school_row['Court_owner'], school_row['Court_qrcodeurl']))

            # 删除本地数据库中不存在于学校数据库的记录
            for court_id in local_mapping:
                if court_id not in school_mapping:
                    local_cursor.execute("DELETE FROM CourtInfo WHERE Court_id = %s", (court_id,))

            # 提交本地数据库的更改
            local_db.commit()
            print("CourtInfo tables synchronized successfully.")

        except Exception as e:
            print(f"Error during synchronization: {e}")
            traceback.print_exc()  # 打印详细错误信息

        finally:
            # 确保关闭数据库连接
            try:
                school_cursor.close()
                school_db.close()
                local_cursor.close()
                local_db.close()
            except:
                pass

        time.sleep(5)