import unittest
from app import app

class TestRoutes(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_home_route(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_dashboard_route(self):
        response = self.client.get('/dashboard')
        self.assertIn(response.status_code, [200, 302])

if __name__ == '__main__':
    unittest.main()
