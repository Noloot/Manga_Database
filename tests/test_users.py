import unittest
from app import create_app
from app.models import db, User
from werkzeug.security import generate_password_hash
import json
from app.utils.util import encode_token

class UserRouteTests(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            
            self.admin_user = User(
                username="admin_user",
                email="admin@email.com",
                password=generate_password_hash("AdminPass123"),
                role="admin"
            )
            db.session.add(self.admin_user)
            
            self.user = User(
                username='JohnDoe', 
                email='jd@email.com', 
                password=generate_password_hash("123"), 
                role='user')
            db.session.add(self.user)
            db.session.flush()
            
            self.regular_user = User(
                username="normal_user",
                email="user@email.com",
                password=generate_password_hash("UserPass123"),
                role="user"
            )
            db.session.add(self.regular_user)
            db.session.commit()
            
            self.user_id = self.user.id
            self.admin_id = self.admin_user.id
            self.user_email = self.user.email
            
            self.user_token = encode_token(str(self.user_id), role='user')
            self.admin_token = encode_token(str(self.admin_id), role='admin')
            
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
        response = self.client.get(
            '/users/',
            headers={'Authorization': f"Bearer {self.admin_token}"}
        )
        self.assertEqual(response.status_code, 200)
        users = response.json.get('users')
        self.assertIsInstance(users, list)
        self.assertGreaterEqual(len(users), 1)
        
    def test_get_user_by_id(self):
        response = self.client.get(
            f'/users/{self.user_id}',
            headers={'Authorization': f"Bearer {self.user_token}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['email'], self.user_email)
        
    def test_get_user_by_invalid_id(self):
        response = self.client.get(
            '/users/9999',
            headers={'Authorization': f"Bearer {self.user_token}"}
        )
        self.assertEqual(response.status_code, 403)
        self.assertIn("Forbidden", response.get_data(as_text=True))
        
    def test_get_users_with_pagination(self):
        response = self.client.get(
            '/users/?page=1&per_page=2',
            headers={'Authorization': f"Bearer {self.admin_token}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('users', response.json)
        
    def test_update_user_by_id(self):
        update_payload = {
            "username": "UpdatedJohn",
            "email": "updated@email.com",
            "password": "UpdatedUser123"
        }
        
        response = self.client.put(
            f'/users/{self.user_id}', 
            json=update_payload,
            headers={'Authorization': f"Bearer {self.user_token}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['username'], 'UpdatedJohn')
        self.assertEqual(response.json['email'], 'updated@email.com')
        
    def test_delete_user_by_id(self):
        response = self.client.delete(
            f'/users/{self.user_id}',
            headers={'Authorization': f"Bearer {self.admin_token}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json)
        
    def test_change_password_success(self):
        payload = {
            "old_password": "123",
            "new_password": "NewPass456"
        }
        
        response = self.client.put(
            "/users/change-password",
            json=payload,
            headers={"Authorization": f"Bearer {self.user_token}"}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("Password changed successfully", response.get_data(as_text=True))
        
    def test_change_user_role_success(self):
        payload = {
            "role": "admin"
        }
        
        response = self.client.put(
            f"/users/role/{self.user_id}",
            json=payload,
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("User role updated to admin", response.get_data(as_text=True))
        
    def test_change_user_role_invalid(self):
        payload = {
            "role": "superstar"
        }
        
        response = self.client.put(
            f"/users/role/{self.user_id}",
            json=payload,
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid role", response.get_data(as_text=True))
        
    def test_get_my_profile(self):
        response = self.client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {self.user_token}"}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['username'], self.user.username)