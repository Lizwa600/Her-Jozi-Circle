import unittest
import sqlite3
import os
from app import app

class TestHerJoziCircle(unittest.TestCase):
    def setUp(self):
        """Set up a test database and client"""
        # Configure app for testing
        self.test_db = 'test_herjozicircle.db'
        app.config.update(
            TESTING=True,
            WTF_CSRF_ENABLED=False,
            DATABASE=self.test_db
        )
        
        # Create test client
        self.app = app.test_client()
        
        # Create test database and tables
        with app.app_context():
            with sqlite3.connect(self.test_db) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL
                    )
                ''')
                # Clear any existing test data
                cursor.execute('DELETE FROM users')
                conn.commit()
    
    def tearDown(self):
        """Clean up after tests"""
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
    
    def test_home_page(self):
        """Test that home page loads"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_user_registration(self):
        """Test user registration"""
        response = self.app.post('/signup', data=dict(
            name='Test User',
            email='test@example.com',
            password='password123'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Events', response.data)
    
    def test_duplicate_email_registration(self):
        """Test registration with duplicate email"""
        # First registration
        self.app.post('/signup', data=dict(
            name='Test User',
            email='duplicate@example.com',
            password='password123'
        ))
        # Second registration with same email
        response = self.app.post('/signup', data=dict(
            name='Another User',
            email='duplicate@example.com',
            password='password456'
        ))
        self.assertIn(b'This email is already registered', response.data)
    
    def test_successful_login(self):
        """Test successful user login"""
        # First register a user
        self.app.post('/signup', data=dict(
            name='Login Test',
            email='login@test.com',
            password='testpass'
        ))
        # Then try to login
        response = self.app.post('/login', data=dict(
            email='login@test.com',
            password='testpass'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Events', response.data)
    
    def test_failed_login(self):
        """Test login with wrong password"""
        response = self.app.post('/login', data=dict(
            email='nonexistent@test.com',
            password='wrongpass'
        ))
        self.assertIn(b'Invalid login', response.data)

if __name__ == '__main__':
    unittest.main()
