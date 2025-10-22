import unittest
from app import db
from app.models import User, Task

class TestModels(unittest.TestCase):
    def test_user_creation(self):
        user = User(name='Test User', email='test@example.com')
        self.assertEqual(user.name, 'Test User')
        self.assertEqual(user.email, 'test@example.com')

    def test_task_creation(self):
        task = Task(title='Test Task')
        self.assertEqual(task.title, 'Test Task')

if __name__ == '__main__':
    unittest.main()
