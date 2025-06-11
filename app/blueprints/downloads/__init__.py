from flask import Blueprint

downloads_bp = Blueprint("downloads_bp", __name__)

from . import routes