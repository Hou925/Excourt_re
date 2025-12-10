import os

import psycopg2
import requests
from flask import Flask
from flask_socketio import SocketIO
from flask_swagger_ui import get_swaggerui_blueprint
from config import Config

socketio = SocketIO(cors_allowed_origins="*")  # 允许跨域

pf_folder = os.path.join(os.getcwd(), Config.PF_PATH)

QR_folder = os.path.join(os.getcwd(), Config.QR_PATH)


def get_pg_conn():
    return psycopg2.connect(
        host=Config.POSTGRES_HOST,
        port=Config.POSTGRES_PORT,
        user=Config.POSTGRES_USER,
        password=Config.POSTGRES_PASSWORD,
        dbname=Config.POSTGRES_DB,
    )


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")
    app.config["PF_FOLDER"] = pf_folder
    app.config["QR_FOLDER"] = QR_folder

    socketio.init_app(app)

    from app.routes import (
        chat,
        exchangecourt,
        friend,
        lost_and_found,
        offercourt,
        student,
        teamup,
        upload,
    )

    swaggerui_blueprint = get_swaggerui_blueprint(
        Config.SWAGGER_URL, Config.API_URL, config={"app_name": "ExCourt API Documentation"}
    )

    app.register_blueprint(swaggerui_blueprint, url_prefix=Config.SWAGGER_URL)

    # 注册蓝图
    app.register_blueprint(student.bp)
    app.register_blueprint(offercourt.bp)
    app.register_blueprint(teamup.bp)
    app.register_blueprint(exchangecourt.bp)
    app.register_blueprint(chat.bp)
    app.register_blueprint(lost_and_found.bp)
    app.register_blueprint(friend.bp)
    app.register_blueprint(upload.bp)

    print(f"Swagger Docs Running on http://localhost:8000{Config.SWAGGER_URL}")
    return app
