from flask import render_template, flash,redirect , url_for , request ,session,jsonify, make_response
from app import app, db, admin,bcrypt
from .forms import LoginForm , RegisterForm, BookingForm
from datetime import datetime
from flask_admin.contrib.sqla import ModelView
from .models import User,Screen,Ticket,Movie,Seat
from flask_admin import BaseView, expose
from flask_wtf import FlaskForm
from flask_login import LoginManager,UserMixin,login_user,login_required,logout_user,current_user
from imdb import IMDb
import stripe
from flask_weasyprint import HTML, render_pdf
from flask_mail import Mail,Message

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT']=465
app.config['MAIL_USE_SSL']=True
app.config['MAIL_USERNAME']='email.sever.josh@gmail.com'
app.config['MAIL_PASSWORD']='123456789Ap'
app.config['MAIL_DEFAULT_SENDER']='email.sever.josh@gmail.com'
app.config['MAIL_MAX_EMAILS']=None
app.config['MAIL_ASCII_ATTACHMENTS']=False
mail = Mail(app)


#View model to add IMDB film details into the movies database.
class UserView(ModelView):

	@expose('/new/', methods=('GET', 'POST'))
	def create_view(self):
		ia = IMDb()
		if request.method == 'POST':

			title = request.form['title']
			movie= ia.search_movie(title)[0]
			ia.update(movie, info = ['main','plot'])
			title=str(movie['title'])
			blurb=str(movie['plot outline'])
			year=int(movie['year'])


			#Finding UK certificate and striping for age only 
			for certificate in movie['certificates']:
				if 'United Kingdom' in certificate:
					certificate = certificate[15:]
					break

			#Getting first 5 actors for main actors
			actors = ""
			num = 0
			for actor in movie['cast']:
				actors += actor['name'] + ", "
				num += 1
				if num >= 4:
					actors = actors[:-2]
					break

			#Formatting director name correctly
			for director in movie['director']:
				director = director['name']
				break

			movie_poster = movie['cover url']
			runtime = int(movie['runtime'][0])

			new_movie = Movie(title=title,blurb=blurb,certificate=certificate,
							runtime=runtime,director=director,
							movie_poster=movie_poster,year=year,cast=actors)

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

stripe.api_key = 'sk_test_51ITU84JRnfjfZwZwgY8i7TcJNu4hv4PY3Fm73LObBLkBc6XuFGHG4rphITY3MWImzJOZi7kL7usQOccRodFXGm1r008lSBDECv'
@app.route('/payment', methods=['GET', 'POST'])
def payment():
    movie = request.form["movie"];
    venue = request.form["venue"];
    date = request.form["date"];
    no_of_tickets = request.form["no_of_tickets"];
    show_no = request.form["show_no"];

    resp = make_response(render_template('payment.html'))
    resp.set_cookie('movie', movie)
    resp.set_cookie('venue', venue)
    resp.set_cookie('date', date)
    resp.set_cookie('no_of_tickets', no_of_tickets)
    resp.set_cookie('show_no', show_no)

    return resp
    
@app.route('/stripe_pay', methods=['GET', 'POST'])
def stripe_pay():
    age = request.cookies.get('venue')
    if (age=="Child (16 and under)"):
        age = 'price_1ITUMJJRnfjfZwZwxWrEWOQR'
    elif(age=="Adult (Above 16)"):
        age = 'price_1ITUNhJRnfjfZwZwmuukV1G9'
    elif(age=="Senior (65 and above)"):
        age = 'price_1ITUO3JRnfjfZwZwu6AK9VOx'
    quant = request.cookies.get('no_of_tickets')
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': age,
            'quantity': quant,
        }],
        mode='payment',
        success_url=url_for('thanks', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('booking', _external=True),
    )
    return {
        'checkout_session_id': session['id'], 
        'checkout_public_key': app.config['STRIPE_PUBLIC_KEY']
    }

@app.route('/thanks')
def thanks():
    return render_template('availability.html')

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

@app.route('/')
def index():
	return redirect(url_for('home'))

@login_required
@app.route('/home')
def home():
	return render_template('home.html')

@app.route('/availability')
def availability():
	return render_template('availability.html')

@app.route('/seats')
def seats():
	return render_template('seats.html')

@app.route('/booking', methods=['GET', 'POST'])
def booking():
	form=BookingForm()
	movies = Movie.query.filter_by().all()	
	form.time.choices=[(time.id) for title in Movie.query.filter_by(title='Movie1').all()]
	return render_template('booking.html', form=form, movies=movies)

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

@app.route('/view_tickets',methods=['GET','POST'])
def view_tickets():
	tickets=Ticket.query.filter_by(user_id=current_user.id) # get all tickets of the current user
	current_time=datetime.now() #get current time to compare it to ticket time
	return render_template('view_tickets.html',tickets=tickets,current_time=current_time)

@app.route('/ticket/<int:ticket_id>/',methods=['GET','POST'])
def ticket_html(ticket_id):
	ticket=Ticket.query.filter_by(id=ticket_id).one()
	return render_template('ticket_pdf.html', ticket=ticket)

@app.route('/ticket/<int:ticket_id>.pdf')
def ticket_pdf(ticket_id):
    return render_pdf(url_for('ticket_html', ticket_id=ticket_id))

@app.route('/send_email/<int:ticket_id>')
def send_email(ticket_id):
	ticket=Ticket.query.filter_by(id=ticket_id).one()
	msg = Message('This is your ticket',recipients = [current_user.email])
	msg.html =  render_template('ticket_pdf.html', ticket=ticket)
	mail.send(msg)
	flash("Ticket sent to email !","success")
	return redirect(url_for('view_tickets'))



	
@app.route('/movie')
def movie_list():

	movies = Movie.query.filter_by().all()

	return render_template('movie_list.html', movies=movies)

@app.route('/view_income')
@login_required
def view_income():
	if current_user.username != 'Owner':
		flash('Email already in use',"danger")
		return redirect(url_for('home'))
	else:
		return render_template('view_income.html')

@app.route('/compare_tickets', methods=['GET','POST'])
@login_required
def compare_tickets():
	if current_user.username != 'Owner':
		flash('Email already in use',"danger")
		return redirect(url_for('home'))
	else:

		if request.method == "POST":
			
			date = request.form['date']
			date = datetime.strptime(date, '%Y-%m-%d')

			movies = Movie.query.filter_by().all()

			movie_title = []
			tickets_sold = []

			for movie in movies:
				value = 0
				for screen in movie.screen_id:
					if screen.screen_time > date:
						value += len(screen.tickets)
					
				movie_title.append(movie.title)
				tickets_sold.append(value)
				
			return render_template('compare_tickets.html',
			movies=movie_title,
			values=tickets_sold,
			date_chosen=True)

		else:
			return render_template('compare_tickets.html',
			date_chosen=False)



@app.route('/movie/<int:movie_id>',methods=['GET','POST'])
def movie_detail(movie_id):

	movie = Movie.query.filter_by(id=movie_id).first()

	# Redirection to homepage when movie not found
	if movie is None:
		flash("The movie you were trying to find isn't being shown right now")
		return redirect(url_for('home'))


	# Gets all the screenings of the movie
	screenings = Screen.query.filter_by(movie=movie).order_by(Screen.screen_time).all()

	# if there are no screenings, the website will display "None"
	if screenings == None:
		screen_list = ["None"]
	else:
		screen_list = []
		i = 0
		# Creating string to display screening information for
		# the next 5 screeening of the movie		
		for screen in screenings:
			if i >= 4:
				break
			elif screen.screen_time < datetime.now():
				continue

			time = "Screen " + str(screen.number) 
			time += " at " + str(screen.screen_time.strftime("%H"))
			time += ":" + str(screen.screen_time.strftime("%M"))
			time += " on " + str(screen.screen_time.strftime("%B"))
			time += " " + str(screen.screen_time.strftime("%d"))
			screen_list.append(time)
			i += 1

	# Passing movie details to template
	return render_template('movie.html',
	id=movie.id,
	title=movie.title,
	year=movie.year,
	poster=movie.movie_poster,
	director=movie.director,
	cast=movie.cast,
	certificate=movie.certificate,
	runtime=movie.runtime,
	blurb=movie.blurb,
	screenings=screen_list)

# Routes the user to the booking page when the book tickets button is pressed
@app.route('/book/<int:movie_id>',methods=['GET','POST'])
def movie_book(movie_id):
	return redirect(url_for('booking'))



if __name__=='__main__':
	app.run(debug=True)
