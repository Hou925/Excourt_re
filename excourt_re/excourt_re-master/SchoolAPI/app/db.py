from contextlib import contextmanager

from flask import current_app
from psycopg2 import Error, pool

# create connection pool
connection_pool = None


def init_db_pool():
    global connection_pool
    try:
        if connection_pool is None:
            connection_pool = pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                host=current_app.config["POSTGRES_HOST"],
                port=current_app.config["POSTGRES_PORT"],
                user=current_app.config["POSTGRES_USER"],
                password=current_app.config["POSTGRES_PASSWORD"],
                dbname=current_app.config["POSTGRES_DB"],
            )
    except Error as e:
        current_app.logger.error(f"Pool initializing error: {e}")
        raise


@contextmanager
def get_db_cursor():
    global connection_pool
    cursor = None
    conn = None

    try:
        if connection_pool is None:
            init_db_pool()

        conn = connection_pool.getconn()
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    except Error as e:
        if conn:
            conn.rollback()
        current_app.logger.error(f"DB error: {e}")
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        current_app.logger.error(f"Unexpected error: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn and connection_pool:
            connection_pool.putconn(conn)


def close_db_pool():
    global connection_pool
    try:
        if connection_pool:
            connection_pool.closeall()
            connection_pool = None
    except Error as e:
        current_app.logger.error(f"Error on pool closing: {e}")
        raise
