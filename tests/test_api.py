import unittest
from app import app

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_api_status(self):
        response = self.client.get('/api/status')
        self.assertIn(response.status_code, [200, 401])

if __name__ == '__main__':
    unittest.main()
