import time
import traceback

import psycopg2

# 配置学校和本地数据库连接
school_db_config = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "800Compact",
    "dbname": "schoolapi",
}

local_db_config = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "800Compact",
    "dbname": "excourt",
}


def sync_court_info():
    while True:
        try:
            school_db = psycopg2.connect(**school_db_config)
            local_db = psycopg2.connect(**local_db_config)

            school_cursor = school_db.cursor()
            local_cursor = local_db.cursor()

            # 查询学校数据库的 CourtInfo 表
            school_cursor.execute("SELECT * FROM CourtInfo")
            school_data = school_cursor.fetchall()
            school_columns = [desc[0] for desc in school_cursor.description]
            school_data = [dict(zip(school_columns, row)) for row in school_data]

            # 查询本地数据库的 CourtInfo 表
            local_cursor.execute("SELECT * FROM CourtInfo")
            local_data = local_cursor.fetchall()
            local_columns = [desc[0] for desc in local_cursor.description]
            local_data = [dict(zip(local_columns, row)) for row in local_data]

            school_mapping = {row["court_id"]: row for row in school_data}
            local_mapping = {row["court_id"]: row for row in local_data}

            # 同步新增和更新的数据
            for court_id, school_row in school_mapping.items():
                if court_id in local_mapping:
                    local_row = local_mapping[court_id]
                    if (
                        school_row["court_state"] != local_row["court_state"]
                        or school_row["court_owner"] != local_row["court_owner"]
                    ):
                        local_cursor.execute(
                            """
                            UPDATE CourtInfo
                            SET Court_state = %s, Court_owner = %s
                            WHERE Court_id = %s
                        """,
                            (
                                school_row["court_state"],
                                school_row["court_owner"],
                                court_id,
                            ),
                        )
                else:
                    local_cursor.execute(
                        """
                        INSERT INTO CourtInfo (Court_id, Court_campus, Court_date, Court_time, Court_no, Court_state, Court_owner, Court_qrcodeurl)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                        (
                            school_row["court_id"],
                            school_row["court_campus"],
                            school_row["court_date"],
                            school_row["court_time"],
                            school_row["court_no"],
                            school_row["court_state"],
                            school_row["court_owner"],
                            school_row["court_qrcodeurl"],
                        ),
                    )

            # 删除本地数据库中不存在于学校数据库的记录
            for court_id in local_mapping:
                if court_id not in school_mapping:
                    local_cursor.execute(
                        "DELETE FROM CourtInfo WHERE Court_id = %s", (court_id,)
                    )

            local_db.commit()
            # print("CourtInfo tables synchronized successfully.")

        except Exception as e:
            print(f"Error during synchronization: {e}")
            traceback.print_exc()

        finally:
            try:
                school_cursor.close()
                school_db.close()
                local_cursor.close()
                local_db.close()
            except:
                pass

        time.sleep(5)
