from app.models import db, User
from app.extensions import ma

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        
    password = ma.String(required=True, load_only=True)
        
user_schema = UserSchema()
users_schema = UserSchema(many=True)


class LoginSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User
        
    username = ma.String(required=True)
    password = ma.String(required=True)
    
login_schema = LoginSchema()