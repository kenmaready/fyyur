#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import babel
from datetime import datetime
import dateutil.parser
import json

from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import Form
import inspect
import logging
from logging import Formatter, FileHandler
from sqlalchemy import func

from forms import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# COMPLETED: connect to a local postgresql database
from config import SQLALCHEMY_DATABASE_URI as dbURI
app.config['SQLALCHEMY_DATABASE_URI'] = dbURI
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# NEW: Association Tables for Arits/Genres and Venue/Genres
Artist_Genres = db.Table('Artist_Genres',
    db.Column('artist_id', db.Integer, db.ForeignKey("Artist.id"), primary_key=True),
    db.Column('genre_name', db.String(120), db.ForeignKey('Genre.name'), primary_key=True)
)

Venue_Genres = db.Table('Venue_Genres',
    db.Column('venue_id', db.Integer, db.ForeignKey("Venue.id"), primary_key=True),
    db.Column('genre_name', db.String(120), db.ForeignKey('Genre.name'), primary_key=True)
)


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # COMPLETED: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='venue', lazy=True)
    genres = db.relationship("Genre", secondary=Venue_Genres, backref=db.backref('venues', lazy=True))

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # COMPLETED: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship("Show", backref='artist', lazy=True)
    genres = db.relationship("Genre", secondary=Artist_Genres, backref=db.backref('artists', lazy=True))

# COMPLETED Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime)
    venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"), nullable=False)

class Genre(db.Model):
    __tablename__ = 'Genre'
    name = db.Column(db.String(120), unique=True, primary_key=True)


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
# helpers;
#----------------------------------------------------------------------------#

# helper function to take results of join search (which is a tuple of two objects) and return a combined dictionary 
# from the two objects
def unpack_shows(show_artist_tuples):
    return list(map(lambda show_artist_tuple: {**vars(show_artist_tuple[0]), **vars(show_artist_tuple[1])}, show_artist_tuples))

# helper function to take in a list of Show dictionaries and return with start_times converted
# from DateTime objects to strings for throughput to pages
def datetimes_to_strings(shows):
    converted_shows = shows
    for show in converted_shows:
      show['start_time'] = show['start_time'].strftime('%Y-%m-%d %H:%M:%S')
    return converted_shows

# helper function to get all relevant "keys" of a Class/Model
def get_class_attrs(class_ref):
  attributes = inspect.getmembers(class_ref, lambda x: not(inspect.isroutine(x)))
  return [x[0] for x in attributes if not(x[0].startswith('_') or x[0].startswith('query'))]

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
  # COMPLETED: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
    data = []
    locations = db.session.query(Venue.city, Venue.state).distinct()
    
    for location in locations:
        venue_list = []
        venues = Venue.query.filter_by(city=location[0], state=location[1]).all()
        
        for venue in venues:
            num_upcoming_shows = Show.query.filter(Show.venue_id == venue.id, Show.start_time > datetime.now()).count()
            venue_list.append({"id": venue.id, "name": venue.name, "num_upcoming_shows": num_upcoming_shows})

        data.append({"city": location[0], "state": location[1], "venues": venue_list})
    
    return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # COMPLETED: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  search_term = request.form.get('search_term','')

  venues = Venue.query.filter(Venue.name.ilike('%{}%'.format(search_term))).all()
  
  data = []
  for venue in venues:
    num_upcoming_shows = Show.query.filter(Show.venue_id == venue.id, Show.start_time > datetime.now()).count()
    data.append({ "id": venue.id, "name": venue.name, "num_upcoming shows": num_upcoming_shows})
  
  response = { "count": len(venues), "data": data}
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # COMPLETED: replace with real venue data from the venues table, using venue_id
 
  venue = Venue.query.get(venue_id)
  if not venue:
    return render_template('errors/404.html')

  past_shows = db.session.query(Show, Artist).join(Artist, Artist.id == Show.artist_id).filter(Show.venue_id == venue_id, Show.start_time <= datetime.now()).all() # results are a list of tuples, consisting of Show and Artist instances
  past_shows = unpack_shows(past_shows) # convert each tuple into a dicionary combining attributes from Show and Artist instances
  past_shows = datetimes_to_strings(past_shows) # replace the datetime objects with strings for passing to page

  upcoming_shows = db.session.query(Show, Artist).join(Artist, Artist.id == Show.artist_id).filter(Show.venue_id == venue_id, Show.start_time > datetime.now()).all() # results are a list of tuples, consisting of Show and Artist instances
  upcoming_shows = unpack_shows(upcoming_shows) # convert each tuple into a dictionary combining atributes from Show and Artist instances
  upcoming_shows = datetimes_to_strings(upcoming_shows) # replace the datetime objects with strings for passing to page

  data = {**venue.__dict__, "past_shows": past_shows, "upcoming_shows": upcoming_shows, "past_shows_count": len(past_shows), "upcoming_shows_count": len(upcoming_shows)}

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # COMPLETED: insert form data as a new Venue record in the db, instead
  # TODO??: modify data to be the data object returned from db insertion

  try:
    venue_params = {}
    venue_params['name'] = request.form.get('name', '')
    venue_params['city'] = request.form.get('city', '')
    venue_params['state'] = request.form.get('state', '')
    venue_params['address'] = request.form.get('address', '')
    venue_params['phone'] = request.form.get('phone', '')
    venue_params['image_link'] = ''
    venue_params['facebook_link'] = request.form.get('facebook_link', '')

    genres = request.form.getlist('genres')
    print(genres)

    venue = Venue(**venue_params)
    for genre in genres:
      genre_object = Genre.query.get(genre)
      # if there is no existing genre by this name, add it to Genre table:
      if not genre_object:
        genre_object = Genre(name = genre)
        db.session.add(genre_object)
      
      # add new Genre(name=genre) to new Venue
      venue.genres.append(genre_object)

    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + venue.name + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + venue.name + ' could not be listed.')
  finally:
    db.session.close()

  # on successful db insert, flash success
  # flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # COMPLETED: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('/pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):

  # COMPLETED: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  success = True

  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash('Venue ' + venue.name + ' was successfully deleted.')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + venue_id + ' could not be found or there was a problem with deleting it.')
    success = False
  finally:
    db.session.close()
    return jsonify({ 'success': success })
    
  return render_template('pages/venues.html')

  # BONUS CHALLENGE (COMPLETED): Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # COMPLETED: replace with real data returned from querying the database

  data = []
  artists = Artist.query.order_by(Artist.name).with_entities(Artist.id, Artist.name).all()
  for artist in artists:
    data.append({ "id": artist[0], "name": artist[1]})

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # COMPLETED: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search_term = request.form.get('search_term','')

  artists = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_term))).all()
  
  data = []
  for artist in artists:
    num_upcoming_shows = Show.query.filter(Show.artist_id == artist.id, Show.start_time > datetime.now()).count()
    data.append({ "id": artist.id, "name": artist.name, "num_upcoming shows": num_upcoming_shows})
  
  response = { "count": len(artists), "data": data}
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # COMPLETED: replace with real venue data from the venues table, using venue_id

  artist = Artist.query.get(artist_id)
  if not artist:
    return render_template('errors/404.html')

  past_shows = db.session.query(Show, Venue).join(Venue, Venue.id == Show.venue_id).filter(Show.artist_id == artist_id, Show.start_time <= datetime.now()).all() # results are a list of tuples, consisting of Show and Artist instances
  past_shows = unpack_shows(past_shows) # convert each tuple into a dicionary combining attributes from Show and Artist instances
  past_shows = datetimes_to_strings(past_shows) # replace the datetime objects with strings for passing to page

  upcoming_shows = db.session.query(Show, Venue).join(Venue, Venue.id == Show.venue_id).filter(Show.artist_id == artist_id, Show.start_time > datetime.now()).all() # results are a list of tuples, consisting of Show and Artist instances
  upcoming_shows = unpack_shows(upcoming_shows) # convert each tuple into a dictionary combining atributes from Show and Artist instances
  upcoming_shows = datetimes_to_strings(upcoming_shows) # replace the datetime objects with strings for passing to page

  data = {**artist.__dict__, "past_shows": past_shows, "upcoming_shows": upcoming_shows, "past_shows_count": len(past_shows), "upcoming_shows_count": len(upcoming_shows)}

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):  
  artist = Artist.query.get(artist_id)
  if artist:
    form = ArtistForm(obj = artist)
    form.state.default = artist.state
    
    # get genres from artist and convert to a list of strings and add to form as selected values
    genre_names = []
    for genre in artist.genres:
      genre_names.append(genre.name)
    
    form.genres.data = genre_names
    return render_template('forms/edit_artist.html', form=form, artist=artist)
  
  # if artist isn't found, send user to 404
  else:
    return render_template('errors/404.html')

  # COMPLETED: populate form with fields from artist with ID <artist_id>

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  print(request.form)
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  # check to bs sure artist exists, if not send user to 404 page
  artist = Artist.query.get(artist_id)
  if not artist:
    return render_template('errors/404.html')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # COMPLETED: populate form with values from venue with ID <venue_id>
  venue = Venue.query.get(venue_id)
  if venue:
    form = VenueForm(obj = venue)
    form.state.default = venue.state

    # get genres from artist and convert to a list of strings and add to form as selected values
    genre_names = []
    for genre in venue.genres:
      genre_names.append(genre.name)
    form.genres.data = genre_names
    
    # if artist isn't found, send user to 404
    return render_template('forms/edit_venue.html', form=form, venue=venue)
  else:
    return render_template('errors/404.html')


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  print(request.form)
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

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

  # on successful db insert, flash success
  flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
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
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  flash('Show was successfully listed!')
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
