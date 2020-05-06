
from flask import Flask
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy

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