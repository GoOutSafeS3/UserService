import datetime
import unittest
from database import User
from utils import add_user
from app import create_app


class UsersUtils(unittest.TestCase):
    @classmethod
    def setUp(self):
        self.app = create_app('TEST').app

    def test_add_user(self):
        new_user = User()
        birth = datetime.datetime.today() - datetime.timedelta(weeks=1600)
        new_user.firstname = 'Chiara'
        new_user.lastname = 'Guidotti'
        new_user.email = 'chiara@example.com'
        new_user.set_password(password='chiara')
        new_user.phone = '23756820'
        new_user.dateofbirth = birth
        json = new_user.to_json()
        with self.app.app_context():
            response = add_user('Chiara', 'Guidotti', 'chiara@example.com', 'chiara', '23756820', birth)
            self.assertNotEquals(response, 500)

    def test_delete_user_(self):
        pass


if __name__ == '__main__':
    unittest.main()