import unittest
from app import create_app
from app.models import db, User
from werkzeug.security import generate_password_hash
import json

class UserRouteTests(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            self.user = User(username='John Doe', email='jd@email.com', password=generate_password_hash("123"), role='user')
            db.session.add(self.user)
            db.session.commit()
            self.user_id = self.user.id
            self.user_email = self.user.email
            
            admin_user = User(
                username="admin_user",
                email="admin@email.com",
                password=generate_password_hash("AdminPass123"),
                role="admin"
            )
            regular_user = User(
                username="normal_user",
                email="user@email.com",
                password=generate_password_hash("UserPass123"),
                role="user"
            )
            db.session.add_all([admin_user, regular_user])
            db.session.commit()
            
    def test_create_user_success(self):
        payload = {
            "username": "new_user",
            "email": "new_user@email.com",
            "password": "NewUser123"
        }
        response = self.client.post("/users/", json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertIn("New user added successfully", response.get_data(as_text=True))
        
    def test_create_user_conflict(self):
        payload = {
            "username": "normal_user",
            "email": "user@email.com",
            "password": "Whatever123"
        }
        response = self.client.post("/users/", json=payload)
        self.assertEqual(response.status_code, 409)
        self.assertIn("Username or email already exists", response.get_data(as_text=True))
        
    def test_login_success(self):
        payload = {
            "username": "normal_user",
            "password": "UserPass123"
        }
        response = self.client.post("/users/login", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Successfully Logged In", response.get_data(as_text=True))
        
    def test_login_invalid(self):
        payload = {
            "username": "normal_user",
            "password": "WrongPass"
        }
        response = self.client.post("/users/login", json=payload)
        self.assertEqual(response.status_code, 401)
        self.assertIn("Invalid username or password", response.get_data(as_text=True))
        
    def test_admin_login_success(self):
        payload = {
            "username": "admin_user",
            "password": "AdminPass123"
        }
        response = self.client.post("/users/login/admin", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Admin Logged in", response.get_data(as_text=True))
        
    def test_admin_login_not_admin(self):
        payload = {
            "username": "normal_user",
            "password": "UserPass123"
        }
        response = self.client.post("/users/login/admin", json=payload)
        self.assertEqual(response.status_code, 403)
        self.assertIn("Access denied", response.get_data(as_text=True))
    
    def test_get_all_users(self):
        response = self.client.get('/users/')
        self.assertEqual(response.status_code, 200)
        users = response.json.get('users')
        self.assertIsInstance(users, list)
        self.assertGreaterEqual(len(users), 1)
        
    def test_get_user_by_id(self):
        response = self.client.get(f'/users/{self.user_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['email'], self.user_email)
        
    def test_get_user_by_invalid_id(self):
        response = self.client.get('/users/9999')
        self.assertEqual(response.status_code, 404)
        self.assertIn("User not found", response.get_data(as_text=True))
        
    def test_get_users_with_pagination(self):
        response = self.client.get('/users/?page=1&per_page=2')
        self.assertEqual(response.status_code, 200)
        self.assertIn('users', response.json)
        
    def test_update_user_by_id(self):
        update_payload = {
            "username": "user_normal",
            "email": "user_new@email.com",
            "password": "PassUser123"
        }
        
        response = self.client.put('users/1', json=update_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['username'], 'user_normal')
        self.assertEqual(response.json['email'], 'user_new@email.com')
        
    def test_delete_user_by_id(self):
        response = self.client.delete(f'/users/{self.user_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json)