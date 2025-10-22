import unittest
from flask_socketio import SocketIOTestClient
from app import app, socketio

class TestSockets(unittest.TestCase):
    def setUp(self):
        self.client = SocketIOTestClient(app, socketio)

    def test_connect(self):
        self.assertTrue(self.client.is_connected())

    def tearDown(self):
        self.client.disconnect()

if __name__ == '__main__':
    unittest.main()
