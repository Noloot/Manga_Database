from flask import Blueprint

chapters_bp = Blueprint("chapters_bp", __name__)

from . import routes