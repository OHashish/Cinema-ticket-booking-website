from flask import render_template, flash,redirect , url_for , request ,session,jsonify, make_response
from app import app, db, admin,bcrypt
from .forms import LoginForm , RegisterForm, BookingForm
import datetime
from flask_admin.contrib.sqla import ModelView
from .models import User,Screen,Ticket,Movie,Seat
from flask_admin import BaseView, expose
from flask_wtf import FlaskForm
from flask_login import LoginManager,UserMixin,login_user,login_required,logout_user,current_user
from imdb import IMDb
import stripe
from flask_weasyprint import HTML, render_pdf
from flask_mail import Mail,Message
import json
import sys

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
			current_movie = Movie.query.filter_by(title=title).first()
			start = datetime.datetime(2020, 5, 17, 9)
			while(start.hour<23 and start.hour>8):
				new_screen = Screen(movie_id=current_movie.id, screen_time=start.strftime("%I:%M %p"))
				db.session.add(new_screen)
				time_change=datetime.timedelta(minutes=current_movie.runtime+30)
				start = start + time_change
				start = start + (datetime.datetime.min - start) % (datetime.timedelta(minutes=15))
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
	if (venue=="Child (16 and under)"):
		resp.set_cookie('price', "5.00")
	elif(venue=="Adult (Above 16)"):
		resp.set_cookie('price', "7.00")
	elif(venue=="Senior (65 and above)"):
		resp.set_cookie('price', "5.00")

	return resp
	
@app.route('/print', methods=['GET', 'POST'])
def print():
	tick_id = request.form["ticketselect"]
	ticket = Ticket.query.filter_by(id=tick_id).first()
	ticket.valid=True
	db.session.commit()
	return redirect(url_for('ticket_pdf', ticket_id=tick_id))

@app.route('/stripe_pay', methods=['GET', 'POST'])
def stripe_pay():
	resp = make_response()
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
		success_url=url_for('seats', _external=True, cc='card'),
		cancel_url=url_for('booking', _external=True),
	)
	return {
		'checkout_session_id': session['id'], 
		'checkout_public_key': app.config['STRIPE_PUBLIC_KEY']
	}

@app.route('/thanks', methods=['POST'])
def thanks():
		
	current_movie = Movie.query.filter_by(title=request.cookies.get('movie')).first()
	moment = request.cookies.get('date') + " " +request.cookies.get('show_no')
	date_time_obj = datetime.datetime.strptime(moment, "%Y-%m-%d %I:%M %p")
	screen = Screen.query.filter_by(movie_id=current_movie.id, screen_time=date_time_obj.strftime("%I:%M %p")).first()
	new_ticket = Ticket(valid=True, quantity=request.cookies.get('no_of_tickets'), movie_id=current_movie.id, user_id=current_user.id, time=date_time_obj, age_type=request.cookies.get('venue'), price=request.cookies.get('price'))
	db.session.add(new_ticket)
	db.session.commit()
	new_seat = request.form["something"]
	seats = []
	seats = new_seat.split(",")
	for seat in seats:
		if not seat=="":
			new_seat_entry = Seat(position=seat, screen_id=screen.id, ticket_id=new_ticket.id)
			db.session.add(new_seat_entry)
	db.session.commit()
	return redirect(url_for('view_tickets'))

@app.route('/emplybook', methods=['GET', 'POST'])
def emplybook():
	current_movie = Movie.query.filter_by(title=request.cookies.get('movie')).first()
	moment = request.cookies.get('date') + " " +request.cookies.get('show_no')
	date_time_obj = datetime.datetime.strptime(moment, "%Y-%m-%d %I:%M %p")
	screen = Screen.query.filter_by(movie_id=current_movie.id, screen_time=date_time_obj.strftime("%I:%M %p")).first()
	new_ticket = Ticket(valid=True, quantity=request.cookies.get('no_of_tickets'), movie_id=current_movie.id, user_id=current_user.id, time=date_time_obj, age_type=request.cookies.get('venue'), price=request.cookies.get('price'))
	db.session.add(new_ticket)
	db.session.commit()

	new_seat = request.form["something"]
	seats = []
	seats = new_seat.split(",")
	for seat in seats:
		if not seat=="":
			new_seat_entry = Seat(position=seat, screen_id=screen.id, ticket_id=new_ticket.id)
			db.session.add(new_seat_entry)
	db.session.commit()
	return redirect(url_for('ticket_pdf', ticket_id=new_ticket.id))

@app.route('/reservation', methods=['POST', 'GET'])
def reservation():
	current_movie = Movie.query.filter_by(title=request.cookies.get('movie')).first()
	moment = request.cookies.get('date') + " " +request.cookies.get('show_no')
	date_time_obj = datetime.datetime.strptime(moment, "%Y-%m-%d %I:%M %p")
	screen = Screen.query.filter_by(movie_id=current_movie.id, screen_time=date_time_obj.strftime("%I:%M %p")).first()
	new_ticket = Ticket(valid=False, quantity=request.cookies.get('no_of_tickets'), movie_id=current_movie.id, user_id=current_user.id, time=date_time_obj, age_type=request.cookies.get('venue'), price=request.cookies.get('price'))
	db.session.add(new_ticket)
	db.session.commit()
	new_seat = request.form["something"]
	seats = []
	seats = new_seat.split(",")
	for seat in seats:
		if not seat=="":
			new_seat_entry = Seat(position=seat, screen_id=screen.id, ticket_id=new_ticket.id)
			db.session.add(new_seat_entry)
	db.session.commit()
	return redirect(url_for('view_tickets'))

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

@app.route('/')
def index():
	return redirect(url_for('home'))

@login_required
@app.route('/home')
def home():
	movies = db.session.query(Movie).all()
	return render_template('home.html', movies=movies)

@app.route('/availability')
def availability():
	return render_template('availability.html')

@app.route('/booking', methods=['GET', 'POST'])
def booking():
	form=BookingForm()
	movies = Movie.query.filter_by().all()
	screens = Screen.query.all()	
	movietitles = []
	movieids = []
	screenids = []
	screentimes = []
	for movie in movies:
		movietitles.append(movie.title)
		movieids.append(movie.id)
	for screen in screens:
		screenids.append(screen.movie_id)
		screentimes.append(screen.screen_time)
	form.time.choices=[(time.id) for title in Movie.query.filter_by(title='Movie1').all()]
	return render_template('booking.html', movietitles=movietitles, movies=movies, form=form, movieids=movieids, screenids=screenids, screentimes=screentimes)

@app.route('/login',methods=['GET','POST'])
def login():
	form=LoginForm()

	if form.validate_on_submit():
		user=User.query.filter_by(email=form.email.data).first()
		if user:
			if bcrypt.check_password_hash(user.password,form.password.data):
				login_user(user,remember=form.remember.data)
				if "employee" in user.username:
					return redirect(url_for('employee'))
				else:
					return redirect(url_for('home'))
		flash('Incorrect username or password. Please try again.','danger')
		return redirect(url_for('login'))


	return render_template('login.html',form=form)

@app.route('/employee')
def employee():
	return render_template('employee.html')



@app.route('/validate')
def validate():
	tickets = Ticket.query.filter_by(valid=False).all()
	tick_ids=[]
	for ticket in tickets:
		tick_ids.append(ticket.id)
	return render_template('validate.html', tick_ids=tick_ids)

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
	tickets=Ticket.query.filter_by(user_id=current_user.id)
	ticket_length = tickets.count()
	screens = Screen.query.all()
	seats = Seat.query.all()
	movies = Movie.query.all()
	seatlist=[]

	for ticket in tickets:
		seat_booked=""
		seat_booked+=str(ticket.id)
		for seat in seats:
			if seat.ticket_id ==ticket.id:
				seat_booked +=seat.position+", "
		seatlist.append(seat_booked)

	#current_time=datetime.now() #get current time to compare it to ticket time
	return render_template('view_tickets.html',seats = seats, seatlist = seatlist, ticket_length=ticket_length, tickets=tickets, movies=movies, screens=screens) 
	#,current_time=current_time)

@app.route('/ticket/<int:ticket_id>/',methods=['GET','POST'])
def ticket_html(ticket_id):
	ticket=Ticket.query.filter_by(id=ticket_id).one()
	seats = Seat.query.all()
	booked_seats="Seat: "
	for seat in seats:
		if seat.ticket_id==ticket.id:
			booked_seats+=seat.position
			booked_seats+=", "

	return render_template('ticket_pdf.html', ticket=ticket, seats=booked_seats[0:-2])

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
			elif datetime.datetime.strptime(screen.screen_time, '%I:%M %p') < datetime.datetime.now():
				continue

			time = "Screen " + str(screen.number) 
			time += " at " + str(screen.screen_time.strftime("%I"))
			time += ":" + str(screen.screen_time.strftime("%M"))
			time += " " + str(screen.screen_time.strftime("%p"))

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
	blurb=movie.blurb)

# Routes the user to the booking page when the book tickets button is pressed
@app.route('/book/<int:movie_id>',methods=['GET','POST'])
def movie_book(movie_id):
	return redirect(url_for('booking'))

@app.route('/seats/<string:cc>', methods=['GET', 'POST'])
def seats(cc):
	moment = request.cookies.get('date') + " " +request.cookies.get('show_no')
	date_time_obj = datetime.datetime.strptime(moment, "%Y-%m-%d %I:%M %p")
	current_movie = Movie.query.filter_by(title=request.cookies.get('movie')).first()
	screen = Screen.query.filter_by(movie_id=current_movie.id).first()
	seats = Seat.query.filter_by().all()
	taken_seats = []
	for seat in seats:
		tickets = Ticket.query.filter_by().all()
		for ticket in tickets:
			if seat.ticket_id == ticket.id:
				if ticket.time == date_time_obj and ticket.movie_id == current_movie.id:
					taken_seats.append(int(seat.position)-1)

	resp=make_response(render_template('seats.html',cc=cc, booked=taken_seats, quantity=request.cookies.get('no_of_tickets')))
	return resp

@app.route('/view_income', methods=['GET','POST'])
@login_required
def view_income():
	if current_user.username != 'Owner':
		flash('You cannot access this site',"danger")
		return redirect(url_for('home'))
	else:
		movies = Movie.query.filter_by().all()
		if request.method == "POST":
			choice=0
			select = request.form.get('myList', None)
			select_movie = request.form.get('myMovie', None)
			#Check if a movie was selected
			#if a movie was not selected display an error message otherwise proceed

			if select_movie == "":
					flash('No movie was selected. Please try again.',"danger")
					return redirect(url_for('view_income'))

			if select_movie:
				select_movie=select_movie.split()

			#Check if a graph is selected
			#if a graph was not selected display an error message
			if select == "":
					flash('Please select a graph to show.',"danger")
					return redirect(url_for('view_income'))

			if select == "week":
				choice=1
				today = datetime.datetime.today()
				if datetime.datetime.strftime(today, '%A')=='Monday':
					chosen_day=today
				else:
				#Get date of last Monday
					for i in range(7,0,-1):
						iterate = today - datetime.timedelta(days=i)
						day_of_the_week=datetime.datetime.strftime(iterate, '%A')
						if day_of_the_week=='Monday':
							chosen_day=iterate
						
				week_ago_days = []
				day_income=[]
				tickets = Ticket.query.filter_by().all()
				#Loop 7 days before chosen date and get total tickets price for each
				#ticket and add them to a list
				#Also , add the 7 days' dates to a list
				total=0
				for i in range(7,0,-1):
					d = chosen_day - datetime.timedelta(days=i)
					date_wo_time = datetime.datetime.strftime(d, '%Y-%m-%d')
					for ticket in tickets:
						ticket_time = datetime.datetime.strftime(ticket.time, '%Y-%m-%d')
						if ticket_time==date_wo_time and ticket.valid==True:
							total=total+int(float(ticket.price)*ticket.quantity)

					day_income.append(total)
					if i==7:
						week_ago=d
					week_ago_days.append(d)

				today_date=chosen_day.strftime('%d-%m-%Y')
				week_ago=week_ago.strftime('%d-%m-%Y')

				return render_template('view_income.html',
				days_income=day_income,
				days=week_ago_days,
				choice=choice
				,movies=movies)
			elif select == "overall":
				choice=2
				today = datetime.datetime.today().strftime ('%Y-%m-%d')
				today = datetime.datetime.strptime(today, '%Y-%m-%d')
				today=today.date()
				sdate = datetime.date(2021, 3, 1)   # start date

				delta = today - sdate       # as timedelta
				graph_days=[]
				for i in range(delta.days + 1):
					day = sdate + datetime.timedelta(days=i)
					graph_days.append(day)

				tickets = Ticket.query.filter_by().all()
				total=0
				total_income=[]
				for one_day in graph_days:
					for ticket in tickets:
						ticket_time = datetime.datetime.strftime(ticket.time, '%Y-%m-%d')
						if ticket_time == str(one_day) and ticket.valid==True:
							total=total+int(float(ticket.price)*ticket.quantity)

					total_income.append(total)


				return render_template('view_income.html',choice=choice,graph_days=graph_days,total_income=total_income,movies=movies)
			elif select_movie[0] == "mv":
				choice=3
				selected_movie = select_movie[1]
				selected_movie = Movie.query.filter_by(id=selected_movie).first()
				movie_title=selected_movie.title
				today = datetime.datetime.today().strftime ('%Y-%m-%d')
				today = datetime.datetime.strptime(today, '%Y-%m-%d')
				today=today.date()
				sdate = datetime.date(2021, 3, 1)   # start date

				delta = today - sdate       # as timedelta
				graph_days=[]
				for i in range(delta.days + 1):
					day = sdate + datetime.timedelta(days=i)
					graph_days.append(day)

				tickets = Ticket.query.filter_by().all()
				total=0
				total_income=[]
				for one_day in graph_days:
					for ticket in tickets:
						ticket_time = datetime.datetime.strftime(ticket.time, '%Y-%m-%d')
						if selected_movie.title==ticket.movie.title:
							if ticket_time == str(one_day):
								total=total+int(float(ticket.price))

					total_income.append(total)


				return render_template('view_income.html',choice=choice,graph_days=graph_days,total_income=total_income,movies=movies,movie_title=movie_title)
			else:
				flash('Please select a graph to show.',"danger")
				return redirect(url_for('view_income'))
		return render_template('view_income.html',movies=movies)

@app.route('/compare_tickets', methods=['GET','POST'])
@login_required
def compare_tickets():
	if current_user.username != 'Owner':
		flash('You cannot access this site',"danger")
		return redirect(url_for('home'))
	else:

		if request.method == "POST":

			start_date = request.form['startDate']
			start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
			end_date = request.form['endDate']
			end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

			movies = Movie.query.filter_by().all()
			tickets = Ticket.query.filter_by().all()

			movie_title = []
			tickets_sold = []

			for movie in movies:
				value = 0
				for ticket in tickets:
					if movie.id == ticket.movie_id and start_date < ticket.time < end_date:
						value += ticket.quantity

				movie_title.append(movie.title)
				tickets_sold.append(value)

			return render_template('compare_tickets.html',
			movies=movie_title,
			values=tickets_sold,
			start_date=start_date,
			end_date=end_date,
			date_chosen=True)

		else:
			return render_template('compare_tickets.html',
			date_chosen =False)
if __name__=='__main__':
	app.run(debug=True)
