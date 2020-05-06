from enum import Enum
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

from app_config import db

# Models
class Genre_Choices(Enum):
    Alternative = 'Alternative'
    Blues = 'Blues'
    Classical = 'Classical'
    Country = 'Country'
    Electronic = 'Electronic'
    Folk = 'Folk'
    Funk = 'Funk'
    Hip_Hop = 'Hip-Hop'
    Heavy_Metal = 'Heavy Metal'
    Instrumental = 'Instrumental'
    Jazz = 'Jazz'
    Musical_Theatre = 'Musical Theatre'
    Pop = 'Pop'
    Punk = 'Punk'
    R_and_B = 'R&B'
    Reggae = 'Reggae'
    Rock_n_Roll = 'Rock n Roll'
    Soul = 'Soul'
    Other = 'Other'

# Association Tables for Arits/Genres and Venue/Genres
Artist_Genres = db.Table('Artist_Genres',
    db.Column('artist_id', db.Integer, db.ForeignKey("Artist.id"), primary_key=True),
    db.Column('genre_name', db.Enum(Genre_Choices), db.ForeignKey('Genre.name'), primary_key=True)
)

Venue_Genres = db.Table('Venue_Genres',
    db.Column('venue_id', db.Integer, db.ForeignKey("Venue.id"), primary_key=True),
    db.Column('genre_name', db.Enum(Genre_Choices), db.ForeignKey('Genre.name'), primary_key=True)
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

    @classmethod
    def search(cls, search_term):
       return cls.query.filter(cls.name.ilike('%{}%'.format(search_term))).all()

    # helper method to get shows for a particular venue
    def get_shows(self, when='upcoming'):
      print(self)
      query = db.session.query(Show, Artist).join(Artist, Artist.id == Show.artist_id)
      if when == 'upcoming':
        shows = query.filter(Show.venue_id == self.id, Show.start_time <= datetime.now()).all()
      if when == 'past':
        shows =query.filter(Show.venue_id == self.id, Show.start_time > datetime.now()).all()
      
      shows = Show.unpack_shows(shows) # convert from tuplpe to splatted dicts 
      shows = Show.datetimes_to_strings(shows) # does what it says on the tin
      return shows

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

    @classmethod
    def search(cls, search_term):
       return cls.query.filter(cls.name.ilike('%{}%'.format(search_term))).all()

    # helper method to get pasat or upcoming shows for a particular artist
    def get_shows(self, when='upcoming'):
      query = db.session.query(Show, Venue).join(Venue, Venue.id == Show.venue_id)
      if when == 'upcoming':
        shows = query.filter(Show.artist_id == self.id, Show.start_time <= datetime.now()).all()
      if when == 'past':
        shows =query.filter(Show.artist_id == self.id, Show.start_time > datetime.now()).all()
      
      shows = Show.unpack_shows(shows) # convert tuples to splatted dicts 
      shows = Show.datetimes_to_strings(shows) # does what it says on the tin

      return shows

    def get_genre_names(self):      
      return list(map(lambda genre: genre.name, self.genres))
    
    def update_genres(self, genre_name_list):
      for genre in self.genres:
        if genre.name not in genre_name_list:
          self.genres.remove(genre)
          print("removed genre {}...".format(genre))
      

# COMPLETED Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime)
    venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"), nullable=False)

    # helper method to unpack tuple search results into splatted dicts with info about a show
    @classmethod
    def unpack_shows(cls, show_artist_tuples):
      return list(map(lambda show_artist_tuple: {**vars(show_artist_tuple[0]), **vars(show_artist_tuple[1])}, show_artist_tuples))

    # helper method to donvert show.start_time from datetime object to tstring
    @classmethod
    def datetimes_to_strings(cls, shows):
      converted_shows = shows
      for show in converted_shows:
        show['start_time'] = show['start_time'].strftime('%Y-%m-%d %H:%M:%S')
      return converted_shows

class Genre(db.Model):
     __tablename__ = 'Genre'
     name = db.Column(db.Enum(Genre_Choices), primary_key=True)