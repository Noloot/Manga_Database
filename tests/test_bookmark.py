import unittest
from app import create_app
from app.models import db, User, Bookmark
from werkzeug.security import generate_password_hash
from app.utils.util import encode_token

class BookmarkRouteTests(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            
            self.user = User(
                username='TestUser',
                email='test@email.com',
                password=generate_password_hash("test123"),
                role='user'
            )
            db.session.add(self.user)
            db.session.commit()
            self.user_id = self.user.id
            self.token = encode_token(str(self.user_id), role='user')
            
            self.other_user = User(
                username='OtherUser',
                email='other@email.com',
                password=generate_password_hash("other123"),
                role='user'
            )
            db.session.add(self.other_user)
            db.session.commit()
            self.other_user_id = self.other_user.id
            self.other_token = encode_token(str(self.other_user_id), role='user')
            
            self.bookmark = Bookmark(
                user_id=self.user_id,
                manga_id='1',
                last_read_chapter="Chapter 1",
                favorited=False
            )
            db.session.add(self.bookmark)
            db.session.commit()
            self.bookmark_id = self.bookmark.id
            
    def test_add_bookmark_success(self):
        payload = {
                "manga_id": "2",
                "last_read_chapter": "Chapter 1",
                "favorited": False
                }
        response = self.client.post(
            "/bookmarks/",
            json=payload,
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(response.status_code, 201)
        print("GET JSON:", response.get_data)
        self.assertIn("Bookmark added successfully", response.get_data(as_text=True))
        
    def test_add_bookmark_duplicate(self):
        payload = {
            "manga_id": "1",
            "last_read_chapter": "Chapter 1",
            "favorited": False
        }
        response = self.client.post(
            "/bookmarks/",
            json=payload,
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(response.status_code, 409)
        self.assertIn("Bookmark already exists", response.get_data(as_text=True))
        
    def test_get_all_bookmark(self):
        response = self.client.get('/bookmarks/?page=1&per_page=10')
        self.assertEqual(response.status_code, 200)
        self.assertIn("bookmarks", response.get_json())
        
    def test_get_my_bookmarks(self):
        response = self.client.get(
            "/bookmarks/user",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue("bookmarks" in response.get_json())
        self.assertGreaterEqual(len(response.get_json()['bookmarks']), 1)
        
    def test_get_bookmark_by_id(self):
        response = self.client.get(
            f"/bookmarks/{self.bookmark_id}",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["manga_id"], 1)
        
    def test_toggle_bookmark_add(self):
        response = self.client.post(
            "/bookmarks/toggle/2",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn("Bookmark added", response.get_data(as_text=True))
        
    def test_toggle_bookmark_remove(self):
        response = self.client.post(
            "/bookmarks/toggle/1",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Bookmark removed", response.get_data(as_text=True))
        
    def test_get_bookmarks_for_manga(self):
        response = self.client.get(
            "/bookmarks/manga/1",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue("bookmarks" in response.get_json())
        
    def test_get_my_bookmarks_no_token(self):
        response = self.client.get("/bookmarks/user")
        self.assertEqual(response.status_code, 401)
        
    def test_update_bookmark(self):
        update_payload = {
            "last_read_chapter": "Chapter Updated",
            "favorited": True
        }
        response = self.client.put(
            f"/bookmarks/{self.bookmark_id}", 
            json=update_payload,
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["last_read_chapter"], "Chapter Updated")
        self.assertTrue(response.get_json()["favorited"])
        
    def test_update_bookmark_unauthorized(self):
        update_payload = {
            "last_read_chapter": "Chapter Updated",
            "favorited": True
        }
        response = self.client.put(
            f"/bookmarks/{self.bookmark_id}",
            json=update_payload,
            headers={"Authorization": f"Bearer {self.other_token}"}
        )
        self.assertEqual(response.status_code, 403)
        self.assertIn("Forbidden", response.get_data(as_text=True))
        
    def test_delete_bookmark(self):
        response = self.client.delete(
            f"/bookmarks/{self.bookmark_id}",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Successfully deleted", response.get_data(as_text=True))
        
    def test_delete_bookmark_unauthorized(self):
        response = self.client.delete(
            f"/bookmarks/{self.bookmark_id}",
            headers={"Authorization": f"Bearer {self.other_token}"}
        )
        self.assertEqual(response.status_code, 403)
        self.assertIn("Forbidden", response.get_data(as_text=True))