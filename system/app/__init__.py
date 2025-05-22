from flask import Flask
from flask_mysqldb import MySQL
from flask_socketio import SocketIO
import os

mysql = MySQL()
socketio = SocketIO(cors_allowed_origins="*")  # 允许跨域

pf_path = 'profiles'
pf_folder = os.path.join(os.getcwd(), pf_path)

QR_path = 'QR'
QR_folder = os.path.join(os.getcwd(), QR_path)

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    app.config['PF_FOLDER'] = pf_folder
    app.config['QR_FOLDER'] = QR_folder

    # 初始化 MySQL
    mysql.init_app(app)
    socketio.init_app(app)

    # 注册蓝图
    from app.routes import student, teamup, offercourt, exchangecourt,chat,lost_and_found,friend,upload
    app.register_blueprint(student.bp)
    app.register_blueprint(offercourt.bp)
    app.register_blueprint(teamup.bp)
    app.register_blueprint(exchangecourt.bp)
    app.register_blueprint(chat.bp)
    app.register_blueprint(lost_and_found.bp)
    app.register_blueprint(friend.bp)
    app.register_blueprint(upload.bp)
    return app
