from flask import Blueprint

bp = Blueprint("courts", __name__)

from app.courts import routes
