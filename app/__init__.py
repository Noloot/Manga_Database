from flask import Flask
from app.models import db
from app.extensions import ma
from app.blueprints.bookmarks import bookmarks_bp
from app.blueprints.users import users_bp
from app.blueprints.manga import manga_bp
from app.blueprints.chapters import chapters_bp
from app.blueprints.downloads import downloads_bp
from app.blueprints.reading_history import reading_history_bp
from config import DevelopmentConfig, TestingConfig, ProductionConfig
from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.yaml'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Manga Database API"
    }
)

config_map = {
    'DevelopmentConfig': DevelopmentConfig,
    'TestingConfig': TestingConfig,
    'ProductionConfig': ProductionConfig
}

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config_map[config_name])
    
    db.init_app(app)
    ma.init_app(app)
    
    app.register_blueprint(bookmarks_bp, url_prefix='/bookmarks')
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(manga_bp, url_prefix='/manga')
    app.register_blueprint(chapters_bp, url_prefix='/chapter')
    app.register_blueprint(downloads_bp, url_prefix='/download')
    app.register_blueprint(reading_history_bp, url_prefix='/history')
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    return app
