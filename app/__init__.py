from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate 
from flask_admin import Admin
from flask_bcrypt import Bcrypt
import logging

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
bcrypt=Bcrypt(app)
log = logging.getLogger('werkzeug')
log.disabled = True
app.logger.disabled = True
app.config['STRIPE_PUBLIC_KEY'] = 'pk_test_51ITU84JRnfjfZwZwEpMJmgofj4yGOyTW6lOyorqQOxONeU2vDRWES4mZ6SIOjBIoVskeWvqzP9NCGV3niNW09cuQ00ijCpqB8X'
app.config['STRIPE_SECRET_KEY'] = 'sk_test_51ITU84JRnfjfZwZwgY8i7TcJNu4hv4PY3Fm73LObBLkBc6XuFGHG4rphITY3MWImzJOZi7kL7usQOccRodFXGm1r008lSBDECv'

migrate = Migrate(app, db)

admin=Admin(app)

from app import views, models
