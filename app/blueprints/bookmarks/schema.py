from app.models import db, Bookmark
from app.extensions import ma
from marshmallow import fields

class BookmarkSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Bookmark
        load_instance = True
        
    user_id = fields.Int(load_only=True)
    manga_id = fields.Int(required=True)
        
bookmark_schema = BookmarkSchema()
bookmarks_schema = BookmarkSchema(many=True)