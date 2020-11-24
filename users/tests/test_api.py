import datetime
import unittest
from werkzeug.security import generate_password_hash, check_password_hash
from users.api import URL_BOOKINGS, URL_RESTAURANTS
from users.app import create_app
import requests_mock


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

    def test_get_negative_users(self):
        client = self.app.test_client()
        response = client.get('/users?is_positive=False')
        self.assertEqual(response.status_code, 200)

    def test_get_users_by_email(self):
        client = self.app.test_client()
        users = {}
        response = client.get('/users?email=anna@example.com', json=users)
        json = response.get_json()
        self.assertEqual(response.status_code, 200, msg=json)
        self.assertEqual(len(json), 1, msg=json)

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

        response = client.get('/users?phone=468333331', json=users)
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
            'password': generate_password_hash('new'),
            'firstname': 'Nuovo',
            'lastname': 'Utente',
            'phone': '345141451',
            'dateofbirth': '1990-10-10',
            'is_admin': False,
            'is_operator':False,
            'is_health_authority':False
        }
        response = client.post('/users', json=new_user)
        json = response.get_json()
        self.assertEqual(response.status_code, 200, msg=json)
        new_user = {
            'email': 'new@example.com',
            'password': generate_password_hash('new'),
            'firstname': 'Nuovo1',
            'lastname': 'Utente1',
            'phone': '345141454',
            'dateofbirth': '1990-12-12',
            'is_admin': False,
            'is_operator': False,
            'is_health_authority': False
        }
        response = client.post('/users', json=new_user)
        json = response.get_json()
        self.assertEqual(response.status_code, 400, msg=json)
        new_user = {
            'email': 'new2@example.com',
            'password': generate_password_hash('new2'),
            'firstname': 'Nuovo2',
            'lastname': 'Utente2',
            'phone': '3451414553',
            'dateofbirth': '1990-10-10',
            'ssn': 'ANNASSN4791DFGYU',
            'is_admin': False,
            'is_operator': False,
            'is_health_authority': False
        }
        response = client.post('/users', json=new_user)
        json = response.get_json()
        self.assertEqual(response.status_code, 400, msg=json)

        new_user = {
            'email': 'new2@example.com',
            'password': generate_password_hash('new2'),
            'firstname': 'Nuovo2',
            'lastname': 'Utente2',
            'phone': '3451414553',
            'dateofbirth': '2021-10-10',
            'is_admin': False,
            'is_operator': False,
            'is_health_authority': False
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
            'password': generate_password_hash('anna'),
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
        response = client.put('/users/999', json=modify_user)
        self.assertEqual(response.status_code, 404)

    def test_edit_user400email(self):
        client = self.app.test_client()
        modify_user = {
            'id': 1,
            'firstname': 'Gianni',
            'lastname': 'Rossi',
            'email': "anna@example.com",
            'password': generate_password_hash('gianni'),
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
            'firstname': 'Daniele',
            'lastname': 'Verdi',
            'email': "daniele@example.com",
            'password': generate_password_hash('daniele'),
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
            'password': generate_password_hash('giada'),
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
            'password': generate_password_hash('giada')
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
            'password': generate_password_hash('anna'),
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

    def test_get_contacts(self):
        client = self.app.test_client()
        with requests_mock.mock() as mock:
            end_ = datetime.datetime.today()
            begin_ = end_ - datetime.timedelta(weeks=2)
            url = URL_BOOKINGS + '/bookings?user_id=2&begin='+str(begin_)+'&end='+str(end_)
            bookings = [{
                'id':3,
                'user_id':2,
                'datetime': str(datetime.datetime.today()-datetime.timedelta(days=8)),
                'restaurant_id': 1,
                'entrance_datetime': str(datetime.datetime.today())
            }]
            mock.get(url, json=bookings)
            rest = {
                'id': 1,
                'occupation_time': 2
            }
            for booking in bookings:
                booking_entrance = booking['entrance_datetime']
                url_rest = URL_RESTAURANTS + '/restaurants/1'
                mock.get(url_rest, json=rest)
                end = datetime.datetime.strptime(booking_entrance[0:9],'%Y-%m-%d') + datetime.timedelta(hours=rest['occupation_time'])
                begin = datetime.datetime.strptime(booking_entrance[0:9],'%Y-%m-%d') - datetime.timedelta(hours=rest['occupation_time'])

                bookings_contact = [{
                    'id': 4,
                    'user_id': 3,
                    'datetime': str(datetime.datetime.today() - datetime.timedelta(days=8)),
                    'restaurant_id': 1,
                    'entrance_datetime': str(datetime.datetime.today())
                }]

                url = URL_BOOKINGS + '/bookings?datetime='+str(booking['datetime'])+'&restaurant_id=1&begin_entrance=' + str(begin) + '&end_entrance=' + str(end)
                mock.get(url, json=bookings_contact)
                reply = client.get('/users/2/contacts?begin='+str(begin_)+'&end='+str(end_))
                print(reply.get_json())
                self.assertEqual(reply.status_code, 200)

    def test_z_delete_user_with_mock(self): # operatore id=8 rest_id=2, provo a cancellare operatore con bookings futuri
        # --------------------------------------------
        # TEST DELETE USER cannot delete operator with future bookings
        # --------------------------------------------
        client = self.app.test_client()
        with requests_mock.mock() as mock:
            bookings = [{
                'id':4,
                'rest_id':1
            }]
            begin = str(datetime.datetime.today())
            url = URL_BOOKINGS +'/bookings?rest_id=2&begin='+begin[0:9]
            mock.get(url, json=bookings)
            reply = client.delete('/users/8')
            self.assertEqual(reply.status_code, 400)

    def test_z_delete_user_with_mock204(self):  # operatore id=7 rest_id=1, provo a cancellare operatore senza bookings
        # --------------------------------------------
        # TEST DELETE USER can delete operator
        # --------------------------------------------
        client = self.app.test_client()
        with requests_mock.mock() as mock:
            no_bookings = []
            begin = str(datetime.datetime.today())
            url = URL_BOOKINGS + '/bookings?rest_id=1&begin=' + begin[0:9]
            mock.get(url, json=no_bookings)
            url_rest = URL_RESTAURANTS + '/restaurants/1'
            response = {'status_code': 204}
            mock.delete(url_rest, json=response)
            reply = client.delete('/users/7')
            print(reply.get_json())
            self.assertEqual(reply.status_code, 201)


if __name__ == '__main__':
    unittest.main()
