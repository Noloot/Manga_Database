from flask import Blueprint

bookmarks_bp = Blueprint("bookmarks_bp", __name__)

from . import routes