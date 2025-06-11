from flask import Blueprint

reading_history_bp = Blueprint("reading_history_bp", __name__)

from . import routes