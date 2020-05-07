#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import babel
import datetime
import dateutil.parser
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_wtf import Form
import inspect
import json
import logging
from logging import Formatter, FileHandler

from app_config import app, db, migrate, moment
from forms import *
from models import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

# moved to ./app_config.py to allow other files access without cross-import issues

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# moved to ./models.py for convenience

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


#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#-----------------------------------------------------------------
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
            num_upcoming_shows = len(venue.get_shows('upcoming'))
            venue_list.append({"id": venue.id, "name": venue.name, "num_upcoming_shows": num_upcoming_shows})

        data.append({"city": location[0], "state": location[1], "venues": venue_list})
    
    return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # COMPLETED: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  search_term = request.form.get('search_term','')
  venues = Venue.search(search_term)
  
  data = []
  for venue in venues:
    num_upcoming_shows = len(venue.get_shows('upcoming'))
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

  past_shows = venue.get_shows('past')
  upcoming_shows = venue.get_shows('upcoming')

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
  
  form = VenueForm(obj=request)
  
  if form.validate():
    try:
      venue_params = {}
      venue_params['name'] = request.form.get('name', '')
      venue_params['city'] = request.form.get('city', '')
      venue_params['address'] = request.form.get('address', '')
      venue_params['state'] = request.form.get('state', '')
      venue_params['phone'] = request.form.get('phone', '')
      venue_params['image_link'] = ''
      venue_params['facebook_link'] = request.form.get('facebook_link', '')
      venue_params['genres'] = [Genre.query.get(genre) for genre in request.form.getlist('genres')]

      venue = Venue(**venue_params)

      db.session.add(venue)
      db.session.commit()
      flash('Venue ' + venue.name + ' was successfully listed!')
    except:
      db.session.rollback()
      flash('An error occurred. Venue ' + request.form.get('name', '') + ' could not be listed.')
    finally:
      db.session.close()
      return render_template('/pages/home.html')

  else:
    return render_template('forms/new_venue.html', form=form)  

  # on successful db insert, flash success
  # flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # COMPLETED: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  

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

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # COMPLETED: populate form with values from venue with ID <venue_id>
  venue = Venue.query.get(venue_id)
  if venue:
    form = VenueForm(obj = venue)
    form.state.default = venue.state
    form.genres.data = [genre.name.value for genre in venue.genres]
    return render_template('forms/edit_venue.html', form=form, venue=venue)
 
  # if venue isn't found send user to 404
  else:
    return render_template('errors/404.html')


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # COMPLETED: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
    venue = Venue.query.get(venue_id)
    if not venue:
      return render_template('errors/404.html')
    
    form = VenueForm(obj=request)
    if form.validate():
      venue.name = request.form.get('name', '')
      venue.city = request.form.get('city', '')
      venue.address = request.form.get('address', '')
      venue.state = request.form.get('state', '')
      venue.phone = request.form.get('phone', '')
      venue.image_link = ''
      venue.facebook_link = request.form.get('facebook_link', '')
      venue.genres = [Genre.query.get(genre) for genre in request.form.getlist('genres')]

      try:
        db.session.commit()
        flash('Venue ' + venue.name + ' has been updated.')
      except:
        db.session.rollback()
        flash('An error occurred. Venue ' + venue.name + ' could not be updated.')
      finally:
        db.session.close() 
        return redirect(url_for('show_venue', venue_id=venue_id))
    
    # if somehow user ended up on a venue id that doesn't exist, send them to 404
    else:
      return render_template('forms/edit_venue.html', form=form, venue=venue)

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

  artists = Artist.search(search_term)
  
  data = []
  for artist in artists:
    num_upcoming_shows = len(artist.get_shows('upcoming'))
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

  past_shows = artist.get_shows('past')
  upcoming_shows = artist.get_shows('upcoming')

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
    form.genres.data = [genre.name.value for genre in artist.genres]
    return render_template('forms/edit_artist.html', form=form, artist=artist)
  
  # if artist isn't found, send user to 404
  else:
    return render_template('errors/404.html')

  # COMPLETED: populate form with fields from artist with ID <artist_id>

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # COMPLETED: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  # check to bs sure artist exists, if not send user to 404 page
    artist = Artist.query.get(artist_id)
    if not artist:
      return render_template('errors/404.html')

    form = ArtistForm(obj = request)
    if form.validate():
      artist.name = request.form.get('name', '')
      artist.city = request.form.get('city', '')
      artist.address = request.form.get('address', '')
      artist.state = request.form.get('state', '')
      artist.phone = request.form.get('phone', '')
      artist.image_link = ''
      artist.facebook_link = request.form.get('facebook_link', '')
      artist.genres = [Genre.query.get(genre) for genre in request.form.getlist('genres')]

      try:
        db.session.commit()
        flash('Artist ' + artist.name + ' has been updated.')
      except:
        db.session.rollback()
        flash('An error occurred. Artist ' + artist.name + ' could not be updated.')
      finally:
        db.session.close() 
        return redirect(url_for('show_artist', artist_id=artist_id))
    
    # if somehow user ended up on a artist id that doesn't exist, send them to 404
    else:
      return render_template('forms/edit_artist.html', form=form, artist=artist)


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # COMPLETED: insert form data as a new Venue record in the db, instead
  # TODO??: modify data to be the data object returned from db insertion
  
  form = ArtistForm(obj=request)
  
  if form.validate():
    try:
      artist_params = {}
      artist_params['name'] = request.form.get('name', '')
      artist_params['city'] = request.form.get('city', '')
      artist_params['state'] = request.form.get('state', '')
      artist_params['phone'] = request.form.get('phone', '')
      artist_params['image_link'] = ''
      artist_params['facebook_link'] = request.form.get('facebook_link', '')
      artist_params['genres'] = [Genre.query.get(genre) for genre in request.form.getlist('genres')]

      artist = Artist(**artist_params)
      db.session.add(artist)
      db.session.commit()

      flash('Artist ' + artist.name + ' was successfully listed!')
    except:
      db.session.rollback()
      flash('An error occurred. Artist ' + request.form.get('name', '') + ' could not be listed.')
    finally:
      db.session.close()
      return render_template('pages/home.html')

  else:
    return render_template('forms/new_artist.html', form=form)  

  # on successful db insert, flash success
  # flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # COMPLETED: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # COMPLETED: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  try:
    shows = Show.get_shows()
  except:
    return render_template('errors/500.html')

  return render_template('pages/shows.html', shows=shows)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # COMPLETED: insert form data as a new Show record in the db, instead
  form = ShowForm(obj=request)
  
  if form.validate():
    show_params = {}
    show_params['artist_id'] = request.form.get('artist_id', '')
    show_params['venue_id'] = request.form.get('venue_id', '')
    start_time = request.form.get('start_time', '')
    show_params['start_time'] = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')

    try:
      show = Show(**show_params)
      print(show)
      db.session.add(show)
      db.session.commit()
      flash('Show was successfully listed!')
    except:
      db.session.rollback()
      flash('An error occurred. Show could not be listed.')
    finally:
      db.session.close()
      return render_template('pages/home.html')

  # on successful db insert, flash success

  # COMPLETED: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  else:
    return render_template('forms/new_show.html', form=form)  

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
