from flask import render_template, flash,redirect , url_for , request ,session,jsonify
from app import app, db, admin,bcrypt
from .forms import LoginForm , RegisterForm
from datetime import datetime
from flask_admin.contrib.sqla import ModelView
from .models import User,Screen,Ticket,Movie,Seat
from flask_admin import BaseView, expose
from flask_wtf import FlaskForm
from flask_login import LoginManager,UserMixin,login_user,login_required,logout_user,current_user
from imdb import IMDb

#View model to add IMDB film details into the movies database.
class UserView(ModelView):

	@expose('/new/', methods=('GET', 'POST'))
	def create_view(self):
		ia = IMDb()
		if request.method == 'POST':

			title = request.form['title']
			movie= ia.search_movie(title)[0]
			ia.update(movie, info = ['main','plot'])
			blurb=str(movie['plot outline'])

			#Finding UK certificate and striping for age only 
			for certificate in movie['certificates']:
				if 'United Kingdom' in certificate:
					certificate = certificate[15:]
					break

			#Formatting director name correctly
			for director in movie['director']:
				director = director['name']
				break

			movie_poster = movie['cover url']
			runtime = int(movie['runtime'][0])

			new_movie = Movie(title=title,blurb=blurb,certificate=certificate,
							runtime=runtime,director=director,
							movie_poster=movie_poster)
			db.session.add(new_movie)
			db.session.commit()

			return redirect('/admin/movie')
		else:
			return self.render('admin/movie_index.html')
		
		
		

#Create all admin Views
admin.add_view(ModelView(User,db.session))
admin.add_view(ModelView(Screen,db.session))
admin.add_view(ModelView(Ticket,db.session))
admin.add_view(ModelView(Seat,db.session))
admin.add_view(UserView(Movie,db.session))




login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

@app.route('/')
def index():
	return render_template('index.html')
	
@login_required
@app.route('/home')
def home():
	return render_template('home.html')

@app.route('/login',methods=['GET','POST'])
def login():
	form=LoginForm()

	if form.validate_on_submit():
		user=User.query.filter_by(email=form.email.data).first()
		if user:
			if bcrypt.check_password_hash(user.password,form.password.data):
				login_user(user,remember=form.remember.data)
				return redirect(url_for('home'))
		flash('Incorrect username or password. Please try again.','danger')
		return redirect(url_for('login'))


	return render_template('login.html',form=form)

@app.route('/signup',methods=['GET','POST'])
def signup():
	form=RegisterForm()
	flag=0
	if form.validate_on_submit():
		hash_pass=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user=User.query.filter_by(username=form.username.data).first()
		email=User.query.filter_by(email=form.email.data).first()
		if user:
			flash('Username already in use',"danger")
			flag=1
		if email:
			flash('Email already in use',"danger")
			flag=1
		if flag==0:
			new_user=User(username=form.username.data,email=form.email.data,password=hash_pass)
			db.session.add(new_user)
			db.session.commit()
			flash("Your account has been created! You can now login","success")
			return redirect(url_for('login'))
	return render_template('signup.html',form=form)

@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for("login"))

if __name__=='__main__':
	app.run(debug=True)
