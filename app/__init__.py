from flask import Flask
from app.models import db
from app.extensions import ma
from app.blueprints.bookmarks import bookmarks_bp
from app.blueprints.users import users_bp
from app.blueprints.manga import manga_bp
from app.blueprints.chapters import chapters_bp
from app.blueprints.downloads import downloads_bp
from config import DevelopmentConfig, TestingConfig, ProductionConfig

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

    return app
