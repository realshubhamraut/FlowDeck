import unittest
from app import app

class TestAuth(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_login_page(self):
        response = self.client.get('/auth/login')
        self.assertEqual(response.status_code, 200)

    def test_register_page(self):
        response = self.client.get('/auth/register')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
