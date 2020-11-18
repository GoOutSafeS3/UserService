import unittest
import datetime
from app import create_app


class UsersTest(unittest.TestCase):
    @classmethod
    def setUp(self):
        self.app = create_app('TEST').app

    def test_get_users(self):
        client = self.app.test_client()
        users = {}
        response = client.get('/users', json=users)
        json = response.get_json()
        self.assertEqual(response.status_code, 200, msg=json)

    def test_get_users_by_email(self):
        client = self.app.test_client()
        users = {}
        response = client.get('/users?email=anna@example.com', json=users)
        json = response.get_json()
        self.assertEqual(response.status_code, 200, msg=json)

    def test_get_users_by_email_2(self):
        client = self.app.test_client()
        users = {}
        response = client.get('/users?email=error@example.com', json=users)
        json = response.get_json()
        self.assertEqual(response.status_code, 404, msg=json)

    def test_get_users_by_ssn(self):
        client = self.app.test_client()
        users = {}
        response = client.get('/users?ssn=ANNASSN4791DFGYU', json=users)
        json = response.get_json()
        self.assertEqual(response.status_code, 200, msg=json)
        response = client.get('/users?ssn=SSNERROR56832ad', json=users)
        json = response.get_json()
        self.assertEqual(response.status_code, 404)

    def test_get_users_by_phone(self):
        client = self.app.test_client()
        users = {}
        response = client.get('/users?phone=46968411', json=users)
        json = response.get_json()
        self.assertEqual(response.status_code, 200, msg=json)

        response = client.get('/users?ssn=468333331', json=users)
        self.assertEqual(response.status_code, 404)

    def test_get_user_id(self):
        client = self.app.test_client()
        user = {}
        response = client.get('/users/1', json=user)
        json = response.get_json()
        self.assertEqual(response.status_code, 200, msg=json)
        response = client.get('/users/999')
        self.assertEqual(response.status_code, 404)

    def test_create_user(self):
        client = self.app.test_client()
        new_user = {
            'email': 'new@example.com',
            'password': 'new',
            'password_repeat':'new',
            'firstname':'Nuovo',
            'lastname':'Utente',
            'phone':'345141451',
            'dateofbirth' : '1990-10-10'
        }
        response = client.post('/users', json=new_user)
        json = response.get_json()
        self.assertEqual(response.status_code, 200, msg=json)
        new_user = {
            'email': 'new@example.com',
            'password': 'new',
            'password_repeat': 'new',
            'firstname': 'Nuovo1',
            'lastname': 'Utente1',
            'phone': '345141454',
            'dateofbirth': '1990-12-12'
        }
        response = client.post('/users', json=new_user)
        json = response.get_json()
        self.assertEqual(response.status_code, 400, msg=json)
        new_user = {
            'email': 'new2@example.com',
            'password': 'new2',
            'password_repeat': 'new2',
            'firstname': 'Nuovo2',
            'lastname': 'Utente2',
            'phone': '3451414553',
            'dateofbirth': '1990-10-10',
            'ssn': 'ANNASSN4791DFGYU'
        }
        response = client.post('/users', json=new_user)
        json = response.get_json()

        self.assertEqual(response.status_code, 400, msg=json)
        new_user = {
            'email': 'new2@example.com',
            'password': 'new2',
            'password_repeat': 'new2',
            'firstname': 'Nuovo2',
            'lastname': 'Utente2',
            'phone': '3451414553',
            'dateofbirth': '2021-10-10'
        }
        response = client.post('/users', json=new_user)
        json = response.get_json()
        self.assertEqual(response.status_code, 400, msg=json)

    def test_z_delete_user(self):
        client = self.app.test_client()
        response = client.delete('/users/1')
        self.assertEqual(response.status_code, 201)

        response = client.delete('/users/999')
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()