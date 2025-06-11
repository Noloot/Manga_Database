from app.models import db, Download
from app.extensions import ma
from marshmallow import fields

class DownloadSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Download
        load_instance = True
    
    user_id = fields.Integer(required=True)
    chapter_id = fields.String(required=True)
        
download_schema = DownloadSchema()
downloads_schema = DownloadSchema(many=True)