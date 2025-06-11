import unittest
from app import create_app
from app.models import db, Chapter, Manga, User
import json
from datetime import datetime
import uuid

class ChapterRouteTests(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            
            self.user = User(username='testuser', email='test@example.com', password='test123')
            db.session.add(self.user)
            db.session.commit()
            self.user_id = self.user.id
            
            self.manga = Manga(
                id=1,
                title="Some Manga",
                author="Author",
                status="Ongoing",
                cover_url="https://example.com/cover.jpg",
                genre="Action",
                book_type="Manga",
                published_date=datetime.today().date(),
                rating=4.5,
                views=100,
                description='Example description'
            )
            
            db.session.add(self.manga)
            db.session.flush()
            self.manga_id = self.manga.id
            db.session.commit()
            
            self.chapter = Chapter(
                id=str(uuid.uuid4()),
                chapter_number='chapter 1', 
                title='Test Title', 
                release_date=datetime.strptime('2025-06-07', '%Y-%m-%d').date(), 
                language='en',
                manga_id=self.manga.id
            )
            db.session.add(self.chapter)
            db.session.commit()
            self.chapter_id = self.chapter.id
            
    def test_create_chapter(self):
        payload = {
            "manga_id": 1,
            "chapter_number": "Chapter 1",
            "title": "Test Title",
            "release_date": "2025-05-05",
            "language": "en"
        }
        
        response = self.client.post("/chapter/", json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertIn("New chapter added successfully", response.get_data(as_text=True))
        
    def test_get_all_chapters(self):
        response = self.client.get('/chapter/')
        self.assertEqual(response.status_code, 200)
        chapters = response.json.get('chapters')
        self.assertIsInstance(chapters, list)
        self.assertGreaterEqual(len(chapters), 1)
        
    def test_get_chapters_by_id(self):
        from app.utils.util import encode_token
        token = encode_token(user_id=self.user_id, role='user')
        
        response = self.client.get(
            f'/chapter/{self.chapter_id}',
            headers={
                "Authorization": f"Bearer {token}"
            }
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['title'], "Test Title")
        self.assertEqual(response.json['release_date'][:10], "2025-06-07")
        
    def test_get_next_chapter(self):
        next_chapter = Chapter(
            chapter_number="chapter 2",
            title="Next Chapter",
            release_date=datetime.strptime('2025-06-10', '%Y-%m-%d').date(),
            language="en",
            manga_id=self.manga_id
        )
        
        with self.app.app_context():
            db.session.add(next_chapter)
            db.session.commit()
        
        response = self.client.get(f'/chapter/{self.chapter_id}/next')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['title'], "Next Chapter")
        
    def test_search_chapter_by_title(self):
        response = self.client.get('/chapter/search?title=Test')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(any("Test" in chapter['title'] for chapter in data))
    
    def test_search_chapter_by_language(self):
        response = self.client.get('/chapter/search?language=en')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(all(ch['language'] == 'en' for ch in data))
        
    def test_get_chapters_by_manga_id(self):
        response = self.client.get(f'/chapter/manga/{self.manga_id}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertTrue(all(ch['manga_id'] == self.manga_id for ch in data))
        self.assertGreaterEqual(len(data), 1)
    
    def test_update_chapter_by_id(self):
        update_payload = {
            "chapter_number": 'chapter 1',
            "title": "Title Test",
            "release_date": "2025-06-09",
            "language": "en",
            "manga_id": 1
        }
        
        response = self.client.put(f'/chapter/{self.chapter_id}', json=update_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['title'], 'Title Test')
        
    def test_delete_chapter(self):
        response = self.client.delete(f'/chapter/{self.chapter_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json)