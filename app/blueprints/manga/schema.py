from app.models import db, Manga
from app.extensions import ma

class MangaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Manga
        load_instance = True
        
manga_schema = MangaSchema()
mangas_schema = MangaSchema(many=True)