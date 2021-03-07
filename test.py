import os
import unittest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app import app, db, models

class TestCase(unittest.TestCase):
    def setUp(self):
        app.config.from_object('config')
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        #the basedir lines could be added like the original db
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.app = app.test_client()
        db.create_all()
        pass


    def tearDown(self):
        db.session.remove()
        db.drop_all()
    
    def test_login_page(self):
        response = self.app.get('/login',
                               follow_redirects=True)
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
        unittest.main()
        app.run()
