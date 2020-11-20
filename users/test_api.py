import unittest
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
            'password_repeat': 'new',
            'firstname': 'Nuovo',
            'lastname': 'Utente',
            'phone': '345141451',
            'dateofbirth': '1990-10-10'
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

    def test_edit_user_mark(self):
        client = self.app.test_client()
        modify_user = {
            'id':3,
            'firstname': 'Anna',
            'lastname': 'Rossi',
            'email': "anna@example.com",
            'old_password': "anna",
            'password': "anna",
            'password_repeat': "anna",
            'phone': "46968411",
            'dateofbirth': "1990-11-11",
            'is_positive': True,
            'ssn': 'ANNASSN4791DFGYU'
        }
        response = client.put('/users/3', json=modify_user)
        json = response.get_json()
        self.assertEqual(response.status_code, 200, msg=json)
        response = client.get('/users?is_positive=True')
        json = response.get_json()
        self.assertNotEqual('[]',json)

    def test_edit_user400email(self):
        client = self.app.test_client()
        modify_user = {
            'id': 1,
            'firstname': 'Admin',
            'lastname': 'Rossi',
            'email': "anna@example.com",
            'old_password': "admin",
            'password': "anna",
            'password_repeat': "anna",
            'phone': "46968411",
            'dateofbirth': "1990-11-11",
            'is_positive': True,
            'ssn': 'ANNASSN4791DFGYU'
        }
        response = client.put('/users/1', json=modify_user)
        json = response.get_json()
        self.assertEqual(response.status_code, 400)
        expected_error = {'detail': 'The email already exist',
                          'status': 400,
                          'title': 'Bad Request',
                          'type': 'about:blank'}
        self.assertDictEqual(json, expected_error)

    def test_edit_user400ssn(self):
        client = self.app.test_client()
        modify_user = {
            'id': 2,
            'firstname': 'Giada',
            'lastname': 'Verdi',
            'email': "giada@example.com",
            'old_password': "operator",
            'password': "anna",
            'password_repeat': "anna",
            'phone': "4696855791",
            'dateofbirth': "1990-11-11",
            'is_positive': True,
            'ssn': 'ANNASSN4791DFGYU'
        }
        response = client.put('/users/2', json=modify_user)
        json = response.get_json()
        print(json)
        self.assertEqual(response.status_code, 400)
        expected_error = {'detail': 'The ssn already exist',
                          'status': 400,
                          'title': 'Bad Request',
                          'type': 'about:blank'}
        self.assertDictEqual(json, expected_error)

    def test_edit_user400phone(self):
        client = self.app.test_client()
        modify_user = {
            'id': 2,
            'firstname': 'Giada',
            'lastname': 'Verdi',
            'email': "giada@example.com",
            'old_password': "operator",
            'password': "anna",
            'password_repeat': "anna",
            'phone': "46968411",
            'dateofbirth': "1990-11-11",
            'is_positive': True
        }
        response = client.put('/users/2', json=modify_user)
        json = response.get_json()
        self.assertEqual(response.status_code, 400)
        expected_error = {'detail': 'The phone already exist',
                          'status': 400,
                          'title': 'Bad Request',
                          'type': 'about:blank'}
        self.assertDictEqual(json, expected_error)

    """
    inserire test su get_user_contacts
    
    """

    def test_z_delete_user(self):
        client = self.app.test_client()
        # --------------------------------------------
        # TEST DELETE USER user not found
        # --------------------------------------------
        param = {
            'email': "giada@example.com",
            'password': "anna"
        }
        response = client.delete('/users/999', json=param)
        json = response.get_json()
        self.assertEqual(response.status_code, 404)
        expected_error = {'detail': 'User not found',
                          'status': 404,
                          'title': 'Not Found',
                          'type': 'about:blank'}
        self.assertDictEqual(json, expected_error)
        # --------------------------------------------
        # TEST DELETE USER cannot delete data until positive
        # --------------------------------------------
        modify_user = {
            'id': 3,
            'firstname': 'Anna',
            'lastname': 'Rossi',
            'email': "anna@example.com",
            'old_password': "anna",
            'password': "anna",
            'password_repeat': "anna",
            'phone': "46968411",
            'dateofbirth': "1990-11-11",
            'is_positive': True,
            'ssn': 'ANNASSN4791DFGYU'
        }
        r = client.put('/users/3', json=modify_user)
        json1 = r.get_json()
        self.assertEqual(r.status_code, 200, msg=json1)
        response = client.get('/users/3')
        response1 = client.delete('/users/3')
        self.assertEqual(response1.status_code, 400)
        expected_error = {'detail': 'You cannot delete your data as long as you are positive',
                          'status': 400,
                          'title': 'Bad Request',
                          'type': 'about:blank'}
        json2 = response1.get_json()
        self.assertDictEqual(json2, expected_error)
        # --------------------------------------------
        # TEST DELETE USER 201
        # --------------------------------------------


if __name__ == '__main__':
    unittest.main()
