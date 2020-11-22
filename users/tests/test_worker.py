from datetime import date
import unittest 
import datetime

from users.utils import *
from users.app import create_app
from users.worker import * 
from users.background import unmark

class RestaurantsWorkerTests(unittest.TestCase):
    """ Tests utility functions with and without mocks """

############################ 
#### setup and teardown #### 
############################ 

    # executed prior to each test 
    def setUp(self): 
        app = create_app("TEST") 
        self.app = app.app 
        self.app.config['TESTING'] = True 

    # executed after each test 
    def tearDown(self): 
        pass 

###############
#### tests #### 
############### 

    def test_worker(self):
        unmark.apply()
