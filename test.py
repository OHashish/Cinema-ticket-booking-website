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

     


# def test_invalid_user_registration_different_passwords(self):
#     response = self.register('patkennedy79@gmail.com', 'FlaskIsAwesome', 'FlaskIsNotAwesome')
#     self.assertIn(b'Field must be equal to password.', response.data)
 
# def logout(self):
#     return self.app.get(
#         '/logout',
#         follow_redirects=True
#     )

    def tearDown(self):
        db.session.remove()
        db.drop_all()
    
    def test_login_page(self):
        response = self.app.get('/login',
                               follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_signup_page(self):
        response = self.app.get('/signup',
                               follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_home_page(self):
        response = self.app.get('/home',
                               follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def sign_up(self,username, email, password, confirm_password):
        return self.app.post(
        '/signup',
        data=dict(username=username,email=email, password=password,confirm_password=confirm_password),
        follow_redirects=True
    )
 
    def login(self, email, password):
        return self.app.post(
            '/login',
            data=dict(email=email, password=password),
            follow_redirects=True
        )

    def test_valid_user_sign_up(self):
        response = self.sign_up('joshboy','joshboy@gmail.com', '12345679', '12345679')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Your account has been created! You can now login', response.data)
    
    def test_invalid_user_sign_up_different_passwords(self):
        response = self.sign_up('joshboy','joshboy@gmail.com', '12345679', '123sasdfdf45679')
        self.assertIn(b'Field must be equal to password.', response.data)
        
        

if __name__ == '__main__':
        unittest.main()
        app.run()
