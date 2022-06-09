#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

# from email.policy import default
# from enum import unique
from distutils.log import error
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sys
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form,FlaskForm
from forms import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate= Migrate(app,db)
# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:@localhost:5432/fyyurapp'
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(),unique =True)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(120), unique=True)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120), unique= True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    # using edit_venue form as ref , 
    genre = db.column(db.String(120))
    website_link =db.Column(db.String(120))
    # from the html file this is a checkbox.this checkbox uses a true or false. where the ticked state is true and not checked false.
    looking_talent = db.Column(db.Boolean,nullable = False, default =False)
    looking_description = db.Column(db.String(120))
    artists=db.relationship('Artist',secondary='shows')
    shows=db.relationship('Show',backref ='venues',lazy = True)

    # here i added the dunder method bellow for debuging purposes
    def __repr__(self):
      return f'<Venue ID: {self.id}, name: {self.name}, phone: {self.phone}>'


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), unique=True)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120), unique =True)
    genre = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120),unique=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    # with the string length, im following the format above of 120 characters
    website_link = db.Column(db.String(120))
    # this checkbox uses a true or false. where the ticked state is true and not checked false
    looking_venue = db.Column(db.Boolean,nullable= False, default= False)
    looking_description = db.Column(db.String(120))
    shows = db.relationship('Show',backref="artist",lazy =True)
    venues=db.relationship('Venue', secondary='shows')
    def __repr__(self):
       return f'<Artist ID: {self.id}, name: {self.name}, phone: {self.phone}>'


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
# here we create a new show model
class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    # here we add the venue_id as a foreign key as the id can be found on the Venue's Page
    # the show links the venue and artist models,as the artist would be perfoming at different venues
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False) 
    # here we add the artist_id as a foreign key as the id can be found on the Artist's Page
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False) 
    start_time = db.Column(db.DateTime,nullable=False,  default=datetime.utcnow)  
    # Adding the line bellow to assit with debugging
    def __repr__(self):
       return f'<Show ID: {self.id}, name: {self.start_time}>'  
    

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  error=False
  try:
    venue = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state)
    for i in venue:
      venue_city = db.session.query(Venue.id, Venue.name).filter(Venue.city == i[0]).filter(Venue.state == i[1])
      data.append({"city": i[0],"state": i[1],"venues": venue_city})
  except:
    db.session.rollback()
    error=True
    print(sys.exc_info())
    
  finally:
    db.session.close()
  if not error:
      return render_template("pages/home.html")
    

  # data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
    
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }]
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search = request.form.get('search_term', '')
  result = Venue.query.filter(Venue.name.ilike("%" + search + "%")).all()
  response = {"count": len(result),"data": result}
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  # here ill be accessing my database and venue table and getting a partcular venue using a venue_id. ill use a get method to access the venue
  # when getting something from the database we can use the get method
  venue_details = Venue.query.get_or_404(venue_id)
  try:
    data={
    "id": venue_id,
    "name": venue_details.name,
    "genres": venue_details.genre,
    "address": venue_details.address,
    "city": venue_details.city,
    "state": venue_details.state,
    "phone": venue_details.phone,
    "website": venue_details.website,
    "facebook_link": venue_details.facebook_link,
    "seeking_talent": venue_details.looking_talent,
    "seeking_description": venue_details.looking_description,
    "image_link": venue_details.image_link,
    "past_shows_count": 1,
    "past_shows": [],
    "upcoming_shows": [],
    "upcoming_shows_count": 0,
       
  }
  except:
    db.session.rollback()
    print(sys.exc_info())
  finally:
    return render_template('pages/show_venue.html', venue=data)
  # data1={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #   "past_shows": [{
  #     "artist_id": 4,
  #     "artist_name": "Guns N Petals",
  #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 2,
  #   "name": "The Dueling Pianos Bar",
  #   "genres": ["Classical", "R&B", "Hip-Hop"],
  #   "address": "335 Delancey Street",
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "914-003-1132",
  #   "website": "https://www.theduelingpianos.com",
  #   "facebook_link": "https://www.facebook.com/theduelingpianos",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 3,
  #   "name": "Park Square Live Music & Coffee",
  #   "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
  #   "address": "34 Whiskey Moore Ave",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "415-000-1234",
  #   "website": "https://www.parksquarelivemusicandcoffee.com",
  #   "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #   "past_shows": [{
  #     "artist_id": 5,
  #     "artist_name": "Matt Quevedo",
  #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [{
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 1,
  # }
  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # below i just created an instance of the venue form
  form = VenueForm()
  # next, get the information from the venue table
  error = False
  
  try:
    # we also want to check if our form is valid during submission
    if form.validate_on_submit():
      # next, add(insert) new venue into the database, by creating a venue object.
      new_venue = Venue(
      name= form.name.data,
      city=form.city.data,
      state=form.state.data,
      address=form.address.data,
      phone=form.phone.data,
      genre=form.genres.data,
      looking_talent=form.seeking_talent.data, 
      looking_description=form.seeking_description.data,
      image_link=form.image_link.data,
      website_link=form.website_link.data,
      facebook_link=form.facebook_link.data
      ) 
      db.session.add(new_venue)
      db.session.commit()
  except:
    error= True
    db.session.rollback()
    print(sys.exc_info())
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  finally:
    db.session.close()
  if not error:
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return redirect(url_for('home'))
  else:
    flash('An error occurred. Venue ' + new_venue.name + ' could not be listed.')
    
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  # ill be deleting a venue based on the venue id
  venue = Venue.query.get_or_404(venue_id)
  error = False
  try:
    db.session.delete(venue)
    db.session.commit()
  except:
    error= True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close
  if not error:
    flash('Venue ' + venue.name + ' was successfully listed!','success')
    return redirect(url_for('home'))
  else:
    flash('An error occurred. Venue ' + venue.name + ' could not be deleted.','error')


  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  # ill be ordering my artists from my artist table  by their id
  artist_data = Artist.query.all()
  data = []
  for i in artist_data:
    # here im creating a dictionary with artist name and id as shown in the dumy data provided
    data.append({"id":i.id, "name":i.name})


  # data=[{
  #   "id": 4,
  #   "name": "Guns N Petals",
  # }, {
  #   "id": 5,
  #   "name": "Matt Quevedo",
  # }, {
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  # }]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search = request.form.get('search_term', '')
  result = Artist.query.filter(Artist.name.ilike("%" + search + "%")).all()
  response = {"count": len(result),"data": result}
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist_details = Artist.query.get_or_404(artist_id)
  artist_data = {}
  artist_data = {
    "id": artist_id,
    "name": artist_details.name,
    "genres": artist_details.genre,
    "city": artist_details.city,
    "state": artist_details.state,
    "phone": artist_details.phone,
    "website":artist_details.website,
    "seeking_venue": artist_details.looking_venue,
    "seeking_description": artist_details.looking_description,
    "image_link": artist_details.image_link,
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  # data1={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "past_shows": [{
  #     "venue_id": 1,
  #     "venue_name": "The Musical Hop",
  #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 5,
  #   "name": "Matt Quevedo",
  #   "genres": ["Jazz"],
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "300-400-5000",
  #   "facebook_link": "https://www.facebook.com/mattquevedo923251523",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "past_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  #   "genres": ["Jazz", "Classical"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "432-325-5432",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 3,
  # }
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=artist_data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # the standard form is user=user.query.get(some_id), where the first user is the object name and the second is the table name and some id is the id of the desired user.
  # create an instrance of the artist form
  form = ArtistForm()
  # we need to access our database for the current artist values using the artist id
  find_artist=Artist.query.get_or_404(artist_id)
  # im using the artist.x method to access the particular attribute im trying to get data for
  error= False
  try:
    # populate the form with data from the database
    form.name.data  = find_artist.name
    form.city.data = find_artist.city
    form.state.data = find_artist.state
    form.phone.data =find_artist.phone
    form.genres.data = find_artist.genre
    form.image_link.data = find_artist.image_link
    form.website_link.data = find_artist.image_link
    form.website_link.data = find_artist.website_link
    form.facebook_link.data = find_artist.facebook_link
  except:
    error= True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close

  if not error:
    flash("form failed to get filed",'error')
    return redirect(url_for(edit_artist))
  # TODO: on unsuccessful
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # creating an instance of the artist form
  form = ArtistForm()
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False
  try:
    if form.validate_on_submit():
      artist = Artist.query.get_404(artist_id)
      # now we need to take those values from the form and update our databasevalues
      artist.name =form.name.data
      artist.city = form.city.data
      artist.state = form.state.data
      artist.phone = form.phone.data
      artist.genre = form.genres.data
      artist.image_link = form.image_link.data
      artist.website_link = form.website_link.data
      artist.facebook_link =form.facebook_link.data
      # now we add the artist to our database
      db.session.add(artist)
      # commiting those changes to the database
      db.session.commit()
  except:
    error= True
    db.session.rollback()
    print(sys.exc_info())

  finally:
    db.session.close
  if not error:
    flash('Your artist has been updated')
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # The logic or code is similar to the one i wrote under edit artist with data from the form. 
  # query form data using the required venue_id
  form = VenueForm()
  venue = Venue.query.get_or_404(venue_id)
  error= False
  try:
    form.name.data  = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.phone.data =venue.phone
    form.genres.data = venue.genre
    form.image_link.data = venue.image_link
    form.website_link.data = venue.image_link
    form.website_link.data = venue.website_link
    form.facebook_link.data = venue.facebook_link
  except:
    error= True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close

  if not error:
    flash("form failed to get filed",'error')
    return redirect(url_for(edit_venue))
  # TODO: populate form with values from venue with ID <venue_id>
  # remove this venue
  return render_template('forms/edit_venue.html', form=form)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # create an instance of the venue form
  form = VenueForm()
  # i just used parts of the code from edit_artist_sunmission, the logic is the same.
  # edit_name= 
  # edit_city = 
  # edit_state =
  # edit_phone= 
  # edit_genre = 
  # edit_image_link = 
  # edit_website_link = 
  # edit_facebook_link = 
  error = False
  try:
    if form.validate_on_submit():
      venue = Artist.query.get_or_404(venue_id )
      # now we need to take those values from the form and update our databasevalues
      venue.name = form.name.data
      venue.city = form.city.data
      venue.state = form.state.data
      venue.phone = form.phone.data
      venue.genre = form.genres.data
      venue.image_link = form.image_link.data
      venue.looking_description = form.seeking_description.data
      venue.website_link = form.website_link.data
      venue.facebook_link =form.facebook_link.data
      db.session.commit()
  except:
    error= True
    db.session.rollback()
    print(sys.exc_info())

  finally:
    db.session.close()
  if not error:
    flash('Your venue has been updated')
    return redirect(url_for('show_venue', venue_id=venue_id))

  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm()
  error = False
  try:
    if form.validate_on_submit():
      new_artist = Artist(
      name= form.name.data,
      city=form.city.data,
      state=form.state.data,
      phone=form.phone.data,
      genre=form.genres.data, 
      looking_description=form.seeking_description.data,
      image_link=form.image_link.data,
      website_link=form.website_link.data,
      facebook_link=form.facebook_link.data
      )
      # now we need to add new_artist to our database
      db.session.add(new_artist)
      # now we have to commit those changes to the database
      db.session.commit()
      # next, add(insert) new venue into the database, by creating a venue object. 
  except:
    error= True
    db.session.rollback()
    print(sys.exc_info())
    # TODO: on unsuccessful db insert, flash an error instead.
  finally:
    db.session.close
  if not error:
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!','success')
  else:
    flash('An error occurred. Venue ' + new_artist.name + ' could not be listed.','error')
  
  
  
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  show=Show.query.all()
  venue =  Venue.query.get_or_404(venue_id)
  artist = Artist.query.get_or_404(artist_id)
  show_data = []
  error = False
  try:
    # from the dumy data  i see that the data passed to the view is a list of dictionarys. 
    # to display the shows i have to loo through each one of them.
    for i in show:
      venue_id =i.venue_id
      artist_id = i.artist_id
      single_show_data = {
      "venue_id": venue_id,
      "venue_name": venue.name,
      "artist_id": artist_id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": str(show.start_time)
    }
    # with everyloop on the shows data, ill add that information to the data dictionary
    show_data.append(single_show_data)
  except:
    db.session.rollback()
    error=True
    print(sys.exc_info())
  finally:
    db.session.close
  if not error:
    return render_template('pages/shows.html', shows=show_data)
  data=[ {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # this is similar to create artist or venue sunmission
  # TODO: insert form data as a new Show record in the db, instead
  # instance of show
  form = ShowForm()
  error = False
  try:
    if form.validate_on_submit():
      new_show = Show(
        venue_id =form.venue_id.data,
        artist_id = form.artist_id.data,
        start_time = form.start_time.data
      )
      db.session.add(new_show)
      db.session.commit()
  except:
    error= True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if not error:
     # on successful db insert, flash success
    flash('Show was successfully listed!','success')
  else:
    flash('An error occurred. Show could not be listed.','error') 

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
