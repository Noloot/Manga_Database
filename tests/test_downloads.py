import unittest
from app import create_app
from app.models import db, Download, Chapter, Manga, User
from datetime import datetime
import json

class DownloadRouteTest(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            
            self.user = User(
                username='testuser',
                email='testuser@example.com',
                password='hashedpassword'
            )
            db.session.add(self.user)
            db.session.commit()
            self.user_id = self.user.id
            
            self.manga = Manga(
                id=1,
                title='Sample Manga',
                author='Author',
                status='Ongoing',
                cover_url='https://example.com/cover.jpg',
                genre='Action',
                book_type='Manga',
                published_date=datetime.today().date(),
                rating=4.5,
                views=100,
                description='Some description'
            )
            db.session.add(self.manga)
            db.session.commit()
            
            
            self.chapter = Chapter(
                chapter_number='chapter 1',
                title='Chapter Title',
                release_date=datetime.today().date(),
                language="en",
                manga_id=self.manga.id
            )
            db.session.add(self.chapter)
            db.session.commit()
            
            self.download = Download(
                user_id=self.user_id,
                chapter_id=self.chapter.id
            )
            db.session.add(self.download)
            db.session.commit()
            
            self.download_id = self.download.id
            self.chapter_id = self.chapter.id
            
    def test_create_download(self):
        payload = {
            'user_id': self.user_id,
            'chapter_id': self.chapter_id
        }
        response = self.client.post("/download/", json=payload)
        self.assertIn(response.status_code, [201, 409])
        
    def test_get_all_downloads(self):
        response = self.client.get("/download/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("downloads", response.get_json())
    
    def test_update_download(self):
        payload = {
            "user_id": self.user_id,
            "chapter_id": self.chapter_id
        }
        response = self.client.put(f"/download/{self.download_id}", json=payload)
        self.assertEqual(response.status_code, 200)
    
    def test_delete_download(self):
        response = self.client.delete(f'/download/{self.download_id}')
        print("STATUS:", response.status_code)
        print('BODY:', response.get_data(as_text=True))
        print("JSON:", response.get_json())
        self.assertEqual(response.status_code, 200)
        self.assertIn("successfully deleted", response.get_data(as_text=True))