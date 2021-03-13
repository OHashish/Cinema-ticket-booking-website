from flask_wtf import FlaskForm
from wtforms import StringField , PasswordField ,BooleanField,SubmitField,TextAreaField, SelectField
from wtforms.validators import DataRequired,Email,Length,EqualTo


class LoginForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(), Email()])
    password= PasswordField('Password',validators=[DataRequired()])
    remember=BooleanField('Remember me')
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username= StringField('Username',validators=[DataRequired(),Length(min=4,max=15)])
    password= PasswordField('Password',validators=[DataRequired(),Length(min=8,max=80)])
    email=StringField('Email',validators=[DataRequired(),Email(),Length(max=50)])
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class BookingForm(FlaskForm):
    title = SelectField('title', choices=[('movie1', 'movie1'), ('movie2', 'movie2'), ('movie3', 'movie3')])
    time = SelectField('runtime', choices=[])
