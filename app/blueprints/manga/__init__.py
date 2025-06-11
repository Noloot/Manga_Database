from flask import Blueprint

manga_bp = Blueprint("manga_bp", __name__)

from . import routes