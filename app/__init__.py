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

migrate = Migrate(app, db)

admin=Admin(app)

from app import views, models
