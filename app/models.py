from app import db
from flask_login import UserMixin

class User(UserMixin,db.Model):
    id =db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(15),unique=True)
    password=db.Column(db.String(80))
    email=db.Column(db.String(50),unique=True)
    age=db.Column(db.Integer)
    tickets=db.relationship("Ticket",backref='user',lazy=True)
    
class Ticket(db.Model):
    id =db.Column(db.Integer,primary_key=True)
    time=db.Column(db.DateTime)
    screen_id= db.Column(db.Integer,db.ForeignKey('screen.id'))
    age_type=db.Column(db.String(50))
    price=db.Column(db.Float)
    seat=db.relationship('Seat',backref='ticket',uselist=False)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'))

class Screen(db.Model):
    id =db.Column(db.Integer,primary_key=True)
    number =db.Column(db.Integer)
    screen_time=db.Column(db.DateTime)
    tickets=db.relationship('Ticket',backref='screen')
    seats=db.relationship("Seat",backref='screen',lazy=True)
    movie=db.relationship("Movie",backref='screen',uselist=False)
    

class Seat(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    position=db.Column(db.String(80))
    availability =db.Column(db.Boolean)
    ticket_id= db.Column(db.Integer,db.ForeignKey('ticket.id'))
    screen_id=db.Column(db.Integer,db.ForeignKey('screen.id'))

class Movie(db.Model):
    id =db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(80))
    year =db.Column(db.Integer)
    blurb =db.Column(db.String(1000))
    director =db.Column(db.String(80))
    cast =db.Column(db.String(100))
    certificate =db.Column(db.String(20))
    runtime =db.Column(db.Integer)
    movie_poster =db.Column(db.String(100))
    screen_id=db.Column(db.Integer,db.ForeignKey('screen.id'))
    
    

