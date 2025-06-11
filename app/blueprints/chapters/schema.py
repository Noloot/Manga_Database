from app.extensions import ma
from app.models import db, Chapter
from marshmallow import fields

class ChapterSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Chapter
        load_instance = True
        
    manga_id = fields.Integer(required=True)
        
chapter_schema = ChapterSchema()
chapters_schema = ChapterSchema(many=True)