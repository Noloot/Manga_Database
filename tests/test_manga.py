import unittest
from app import create_app
from app.models import db, Manga, User
import json
from werkzeug.security import generate_password_hash
from app.utils.util import encode_token
from datetime import date

class MangaRouteTests(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.commit()
            
            self.admin_user = User(
                username='TestAdmin',
                email='admin@email.com',
                password=generate_password_hash("admin123"),
                role='admin'
            )
            db.session.add(self.admin_user)
            db.session.commit()
            self.admin_user_id = self.admin_user.id
            self.token = encode_token(str(self.admin_user_id), role='admin')
            
            self.manga = Manga(
                id=1,
                title="Test Title",
                author="Test Author",
                status="Ongoing",
                cover_url="https://example.com/default-cover.jpg",
                genre="Action",
                book_type="Manga",
                published_date=date(2025, 6, 2),
                rating=4.75,
                views=100,
                description="Test Description"
            )
            
            self.manga_id = self.manga.id
            self.manga_title = self.manga.title
            db.session.add(self.manga)
            db.session.commit()
            
    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            
    def test_create_manga(self):
        payload = {
            "title": "Title Test",
            "author": "Author Test",
            "status": "Ongoing",
            "cover_url": "https://example.com/test-cover.jpg",
            "genre": "Action",
            "book_type": "Manga",
            "published_date": "2025-06-05",
            "rating": 4.15,
            "views": 100,
            "description": "Description Test"
        }
        
        response = self.client.post(
            "/manga/", 
            json=payload,
            headers={'Authorization': f"Bearer {self.token}"}
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn("New manga added successfully", response.get_data(as_text=True))
        
    def test_create_manga_forbidden_for_user(self):
        with self.app.app_context():
            user = User(
                username='TestUser',
                email='user@email.com',
                password=generate_password_hash("user123"),
                role='user'
            )
            db.session.add(user)
            db.session.commit()
            user_token = encode_token(str(user.id), role='user')
            
        payload = {
            "title": "Forbidden Test",
            "author": "Author Test",
            "status": "Ongoing",
            "cover_url": "https://example.com/test-cover.jpg",
            "genre": "Action",
            "book_type": "Manga",
            "published_date": "2025-06-05",
            "rating": 4.15,
            "views": 100,
            "description": "Description Test"
        }
        response = self.client.post(
            "/manga/",
            json=payload,
            headers={'Authorization': f"Bearer {user_token}"}
        )
        self.assertEqual(response.status_code, 403)
        
    def test_create_manga_no_token(self):
        payload = {
            "title": "No Token Test",
            "author": "Author Test",
            "status": "Ongoing",
            "cover_url": "https://example.com/test-cover.jpg",
            "genre": "Action",
            "book_type": "Manga",
            "published_date": "2025-06-05",
            "rating": 4.15,
            "views": 100,
            "description": "Description Test"
        }
        response = self.client.post("/manga/", json=payload)
        self.assertEqual(response.status_code, 401)
        
    def test_create_manga_duplicate(self):
        payload = {
            "title": "Test Title",
            "author": "Test Author",
            "status": "Ongoing",
            "cover_url": "https://example.com/test-cover.jpg",
            "genre": "Action",
            "book_type": "Manga",
            "published_date": "2025-06-05",
            "rating": 4.15,
            "views": 100,
            "description": "Description Test"
        }
        
        response = self.client.post(
            "/manga/", 
            json=payload,
            headers={'Authorization': f"Bearer {self.token}"}
        )
        self.assertEqual(response.status_code, 409)
        self.assertIn("Manga already exists", response.get_data(as_text=True))
        
    def test_get_all_mangas(self):
        response = self.client.get('/manga/')
        self.assertEqual(response.status_code, 200)
        mangas = response.json.get('mangas')
        self.assertIsInstance(mangas, list)
        self.assertGreaterEqual(len(mangas), 1)
        
    def test_get_manga_by_id(self):
        response = self.client.get(f'/manga/{self.manga_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['title'], self.manga_title)
        
    def test_update_manga_by_id(self):
        update_payload = {
            "title": "Title Test",
            "author": "Author Test",
            "status": "Ongoing",
            "cover_url": "https://example.com/test-cover.jpg",
            "genre": "Action",
            "book_type": "Manga",
            "published_date": "2025-06-05",
            "rating": 4.15,
            "views": 100,
            "description": "Description Test"
        }
        
        response = self.client.put(
            '/manga/1', 
            json=update_payload,
            headers={'Authorization': f"Bearer {self.token}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['title'], 'Title Test')
        self.assertEqual(response.json['author'], 'Author Test')
        
    def test_update_manga_forbidden(self):
        with self.app.app_context():
            user = User(
                username='TestUser',
                email='user@email.com',
                password=generate_password_hash("user123"),
                role='user'
            )
            db.session.add(user)
            db.session.commit()
            user_token = encode_token(str(user.id), role='user')
        response = self.client.put(
            f"/manga/{self.manga_id}",
            headers={'Authorization': f"Bearer {user_token}"}
        )
        self.assertEqual(response.status_code, 403)
        
    def test_delete_manga(self):
        response = self.client.delete(
            f'/manga/{self.manga_id}',
            headers={'Authorization': f"Bearer {self.token}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json)
    
    def test_delete_manga_forbidden(self):
        with self.app.app_context():
            user = User(
                username='TestUser',
                email='user@email.com',
                password=generate_password_hash("user123"),
                role='user'
            )
            db.session.add(user)
            db.session.commit()
            user_token = encode_token(str(user.id), role='user')
            
        response = self.client.delete(
            f"/manga/{self.manga_id}",
            headers={'Authorization': f"Bearer {user_token}"}
        )
        self.assertEqual(response.status_code, 403)
    
    def test_delete_manga_no_token(self):
        response = self.client.delete(f"/manga/{self.manga_id}")
        self.assertEqual(response.status_code, 401)