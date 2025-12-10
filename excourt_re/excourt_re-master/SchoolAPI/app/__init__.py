from flask import Flask

from app.db import close_db_pool, init_db_pool
from config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Init pool on start app
    with app.app_context():
        init_db_pool()

    # Register close pool
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        close_db_pool()

    # register blueprints
    from app.courts import bp as courts_bp
    from app.students import bp as students_bp

    app.register_blueprint(students_bp, url_prefix="/students")
    app.register_blueprint(courts_bp, url_prefix="/courts")

    return app
