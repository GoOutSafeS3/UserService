import datetime
import unittest
from users.database import User
from users.utils import add_user, get_from
from users.app import create_app


class UsersUtils(unittest.TestCase):
    @classmethod
    def setUp(self):
        self.app = create_app('TEST').app

    def test_add_user(self):
        with self.app.app_context():
            birth = datetime.datetime.today() - datetime.timedelta(weeks=1600)
            response = add_user('Chiara', 'Guidotti', 'chiara@example.com', 'chiara', '23756820', birth)
            self.assertNotEqual(response, 500)

    def test_get_from_url(self):
        client = self.app.test_client()
        json, status_code = get_from('127.0.0.1:8081/users', params={'is_positive': True})
        response = client.get('/users?is_positive=True')
        json1 = response.get_json()
        #self.assertEqual(json, json1)

    def test_delete_user_(self):
        pass


if __name__ == '__main__':
    unittest.main()  # pragma: no cover
