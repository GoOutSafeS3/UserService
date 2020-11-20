import requests

USER_SERVICE = "http://localhost:8081"
TIMEOUT = 1


def _get(url):
    """ Makes a get request with a timeout.
    Returns the json object if with the status code (or None, None in case of timeout).
    """
    try:
        r = requests.get(url, timeout=TIMEOUT)
        try:
            return r.json(), r.status_code
        except:
            return None, r.status_code
    except:
        return None, None


def _post(url, json):
    """ Makes a post request with a timeout.
    Returns the json object if with the status code (or None, None in case of timeout).
    """
    try:
        r = requests.post(url, json=json, timeout=TIMEOUT)
        try:
            return r.json(), r.status_code
        except:
            return None, r.status_code
    except:
        return None, None


def _put(url, json):
    """ Makes a put request with a timeout.
    Returns the json object if with the status code (or None, None in case of timeout).
    """
    try:
        r = requests.put(url, json=json, timeout=TIMEOUT)
        try:
            return r.json(), r.status_code
        except:
            return None, r.status_code
    except:
        return None, None


def _delete(url):
    """ Makes a delete request with a timeout.
    Returns the json object if with the status code (or None, None in case of connection error).
    """
    try:
        r = requests.delete(url, timeout=TIMEOUT)
        try:
            return r.json(), r.status_code
        except:
            return None, r.status_code
    except:
        return None, None


def get_users(ssn=None, phone=None, email=None, is_positive=None):
    url = USER_SERVICE + '/users?'

    if ssn is not None:
        url += 'ssn=' + str(ssn) + '&'

    if phone is not None:
        url += 'phone=' + str(phone) + '&'

    if email is not None:
        url += 'email=' + str(email) + '&'

    if is_positive is not None:
        url += 'is_positive=True'

    return _get(url=url)


def get_user(user_id):
    url = USER_SERVICE + '/users/' + str(user_id)
    return _get(url=url)


def create_user(dict_user):
    url = USER_SERVICE + '/users'
    return _post(url=url, json=dict_user)


def edit_user(user_id, dict_user):
    url = USER_SERVICE + '/users'+str(user_id)
    return _put(url=url, json=dict_user)


def delete_user(user_id):
    url = USER_SERVICE + '/users/' + str(user_id)
    return _delete(url)


def get_user_contacts(user_id, begin=None, end=None):
    url = USER_SERVICE + '/users/'+ str(user_id)+'/contacts?'
    if begin is not None and end is not None:
        url+= 'begin='+str(begin)+'&'
        url += 'end=' + str(end)
    return _get(url)


if __name__ == "__main__":
    new_user = {
        'email': 'ciao@example.com',
        'password': 'ciao',
        'password_repeat': 'ciao',
        'firstname': 'Gianni',
        'lastname': 'Utente',
        'phone': '3451414431',
        'dateofbirth': '1990-10-10'
    }
    print(create_user(new_user))
    print(get_users())
    print(get_user(1))
    print(get_user(2))
    print(delete_user(2))