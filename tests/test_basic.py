import os 
import unittest

 
from app import app
import database

TEST_DB = 'test'

class BasicTests(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        
    def tearDown(self):
        pass

    def test_main_page(self):
        response = app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()