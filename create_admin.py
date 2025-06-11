from app import create_app
from app.models import db, User
from werkzeug.security import generate_password_hash
from sqlalchemy import select

app = create_app('DevelopmentConfig')

with app.app_context():
    
    username='Many0106'
    email='marcqueztookes@outlook.com'
    password=generate_password_hash('Marcquez00@')
    
    existing_admin = db.session.execute(
        select(User).where((User.username == username) | (User.email == email))
    ).scalar_one_or_none()
    
    if existing_admin:
        print("Admin already exists. No action taken.")
    else:
        admin = User(
            username=username,
            email=email,
            password=password,
            role='admin'
        )
    
        db.session.add(admin)
        db.session.commit()
        print("Admin user created.")