import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database

# TODO IMPLEMENT DATABASE URL
dialect = "postgres"
username = 'udacity'
password = 'udacity'
dbname = 'fyyurdb'
port = 5432

SQLALCHEMY_DATABASE_URI = "{dialect}://{username}:{password}@localhost:{port}/{dbname}".format(dialect=dialect, username=username, password=password, port=port, dbname=dbname)

