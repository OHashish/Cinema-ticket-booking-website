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
    valid=db.Column(db.Boolean)
    time=db.Column(db.DateTime)
    age_type=db.Column(db.String(50))
    quantity=db.Column(db.Integer)
    price=db.Column(db.String(15))
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'))
    movie_id= db.Column(db.Integer,db.ForeignKey('movie.id'))
    seat=db.relationship('Seat',backref='ticket',uselist=False)
    


class Screen(db.Model):
    id =db.Column(db.Integer,primary_key=True)
    screen_time=db.Column(db.String(15))
    seats=db.relationship("Seat",backref='screen',lazy=True)
    movie_id=db.Column(db.Integer, db.ForeignKey('movie.id'))
    

class Seat(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    position=db.Column(db.String(80))
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
    ticket_id=db.relationship('Ticket',backref='movie', lazy=True, uselist=False)
    screen_id=db.relationship("Screen",backref='movie', lazy=True, uselist=False)
    
    

