from app.models import db, ReadingHistory
from app.extensions import ma

class ReadingHistorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ReadingHistory
        load_instance = True
        
reading_history_schema = ReadingHistorySchema()
reading_histories_schema = ReadingHistorySchema(many=True)
