# Script to populate new db with new data (data matches up with fake data from exercise starter script)
# for dev/setup purposes only
# WARNING: THIS SCRIPT ERASES ALL EXISTING DATA IN DATABASE (LEAVING TABLES INTACT)

import sys
import os

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from app import db
from models import *

# tool to clear all data from database while leaving schema intact:
def clear_data(session):
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print('Clearing table {tablename}...'.format(tablename=table))
        session.execute(table.delete())
    session.commit()

# clear all data - WARNING: THIS WILL DELETE ALL EXISTING DATA: 
# USE WITH CAUTION
clear_data(db.session)
db.session.execute('ALTER SEQUENCE "Artist_id_seq" RESTART WITH 1')
db.session.execute('ALTER SEQUENCE "Venue_id_seq" RESTART WITH 1')
db.session.execute('ALTER SEQUENCE "Show_id_seq" RESTART WITH 1')

artist_data = [
    {
        "name": "Guns N Petals",
        "city": "San Francisco",
        "state": "CA",
        "phone": "326-123-5000",
        "website": "https://www.gunsnpetalsband.com",
        "facebook_link": "https://www.facebook.com/GunsNPetals",
        "seeking_venue": True,
        "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
        "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    },
    {
        "name": "Matt Quevedo",
        "city": "New York",
        "state": "NY",
        "phone": "300-400-5000",
        "facebook_link": "https://www.facebook.com/mattquevedo923251523",
        "seeking_venue": False,
        "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80"
    },
    {
        "name": "The Wild Sax Band",
        "city": "San Francisco",
        "state": "CA",
        "phone": "432-325-5432",
        "seeking_venue": False,
        "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80"
    }
]

venue_data = [
    {
        "name": "The Musical Hop",
        "address": "1015 Folsom Street",
        "city": "San Francisco",
        "state": "CA",
        "phone": "123-123-1234",
        "website": "https://www.themusicalhop.com",
        "facebook_link": "https://www.facebook.com/TheMusicalHop",
        "seeking_talent": True,
        "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
        "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
    },
    {
        "name": "The Dueling Pianos Bar",
        "address": "335 Delancey Street",
        "city": "New York",
        "state": "NY",
        "phone": "914-003-1132",
        "website": "https://www.theduelingpianos.com",
        "facebook_link": "https://www.facebook.com/theduelingpianos",
        "seeking_talent": False,
        "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80"
    },
    {
        "name": "Park Square Live Music & Coffee",
        "address": "34 Whiskey Moore Ave",
        "city": "San Francisco",
        "state": "CA",
        "phone": "415-000-1234",
        "website": "https://www.parksquarelivemusicandcoffee.com",
        "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
        "seeking_talent": False,
        "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80"
    }
]

genre_data = [{ "name": choice.name } for choice in Genre_Choices]

show_data = [
    {
        "start_time": "2019-05-21T21:30:00.000Z",
        "venue_id": 1,
        "artist_id": 1 
    },
    {
        "start_time": "2019-06-15T23:00:00.000Z",
        "venue_id": 3,
        "artist_id": 2 
    },
    {
        "start_time": "2019-04-08T20:00:00.000Z",
        "venue_id": 3,
        "artist_id": 3
    },
    {
        "start_time": "2035-04-08T20:00:00.000Z",
        "venue_id": 3,
        "artist_id": 3
    },
    {
        "start_time": "2035-04-15T20:00:00.000Z",
        "venue_id": 3,
        "artist_id": 3
    },
    {
        "start_time": "2035-04-15T20:00:00.000Z",
        "venue_id": 3,
        "artist_id": 3
    }
]

artist_genre_data = [
    { "artist_id": 1, "genre_name": "Rock_n_Roll"},
    { "artist_id": 2, "genre_name": "Jazz"},
    { "artist_id": 3, "genre_name": "Jazz"},
    { "artist_id": 3, "genre_name": "Classical"}
]

venue_genre_data = [
    { "venue_id": 1, "genre_name": "Jazz"},
    { "venue_id": 1, "genre_name": "Reggae"},
    { "venue_id": 1, "genre_name": "Musical_Theatre"},
    { "venue_id": 1, "genre_name": "Classical"},
    { "venue_id": 1, "genre_name": "Folk"},
    { "venue_id": 2, "genre_name": "Classical"},
    { "venue_id": 2, "genre_name": "R_and_B"},
    { "venue_id": 2, "genre_name": "Hip_Hop"},
    { "venue_id": 3, "genre_name": "Rock_n_Roll"},
    { "venue_id": 3, "genre_name": "Jazz"},
    { "venue_id": 3, "genre_name": "Classical"},
    { "venue_id": 3, "genre_name": "Folk"}
]


def populate_table(data, model):
    for item in data:
        entry = model(**item)
        db.session.add(entry)
        print("New element added to {}...".format(model))
    print("Finished populating {}...".format(model))
        

populate_table(artist_data, Artist)
populate_table(venue_data, Venue)
populate_table(genre_data, Genre)
populate_table(show_data, Show)


for entry in artist_genre_data:
    artist = Artist.query.filter_by(id=entry['artist_id']).one()
    genre = Genre.query.filter_by(name=entry['genre_name']).one()
    artist.genres.append(genre)

print("Finished adding artist genres...")

for entry in venue_genre_data:
    venue = Venue.query.filter_by(id=entry['venue_id']).one()
    genre = Genre.query.filter_by(name=entry['genre_name']).one()
    venue.genres.append(genre)

print("Finished adding venue genres...")


db.session.commit()
