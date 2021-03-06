import re

from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField
from wtforms.validators import DataRequired, AnyOf, Regexp, Optional, URL, ValidationError

from models import Genre_Choices

# ------------------------------------------------------------------------------
# Custom validators
# ------------------------------------------------------------------------------

class PhoneValidator:
  """
  Checks the field's data matches a phone number format (not very robust, this is a prototype)
  """

  def __call__(self, form, field):  
    phone_regex = "(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).*?"
    result = re.match(phone_regex, field.data)

    if not result:
      message = field.gettext("Please provide a valid phone number.")
      raise ValidationError(message)

class ImageLinkValidator:
  """
  Checks the field's data matches a url for an image (allows for ?querystrings after the jpg/gif/png)
  """

  def __call__(self, form, field):
    image_link_regex = "^https?://(?:[a-z0-9\-]+\.)+[a-z]{2,6}(?:/[^/#?]+)+\.(?:jpg|gif|png|jpeg|JPG|GIF|PNG|JPEG)$"
    result = re.match(image_link_regex, field.data)

    if not result:
      message = field.gettext("The image link provided is not a valid link to an image")
      raise ValidationError(message)

# ------------------------------------------------------------------------------
# Forms
# ------------------------------------------------------------------------------

class ShowForm(FlaskForm):
    artist_id = StringField(
        'artist_id'
    )
    venue_id = StringField(
        'venue_id'
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default= datetime.today()
    )

class VenueForm(FlaskForm):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=[
            ('AL', 'AL'),
            ('AK', 'AK'),
            ('AZ', 'AZ'),
            ('AR', 'AR'),
            ('CA', 'CA'),
            ('CO', 'CO'),
            ('CT', 'CT'),
            ('DE', 'DE'),
            ('DC', 'DC'),
            ('FL', 'FL'),
            ('GA', 'GA'),
            ('HI', 'HI'),
            ('ID', 'ID'),
            ('IL', 'IL'),
            ('IN', 'IN'),
            ('IA', 'IA'),
            ('KS', 'KS'),
            ('KY', 'KY'),
            ('LA', 'LA'),
            ('ME', 'ME'),
            ('MT', 'MT'),
            ('NE', 'NE'),
            ('NV', 'NV'),
            ('NH', 'NH'),
            ('NJ', 'NJ'),
            ('NM', 'NM'),
            ('NY', 'NY'),
            ('NC', 'NC'),
            ('ND', 'ND'),
            ('OH', 'OH'),
            ('OK', 'OK'),
            ('OR', 'OR'),
            ('MD', 'MD'),
            ('MA', 'MA'),
            ('MI', 'MI'),
            ('MN', 'MN'),
            ('MS', 'MS'),
            ('MO', 'MO'),
            ('PA', 'PA'),
            ('RI', 'RI'),
            ('SC', 'SC'),
            ('SD', 'SD'),
            ('TN', 'TN'),
            ('TX', 'TX'),
            ('UT', 'UT'),
            ('VT', 'VT'),
            ('VA', 'VA'),
            ('WA', 'WA'),
            ('WV', 'WV'),
            ('WI', 'WI'),
            ('WY', 'WY'),
        ]
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    phone = StringField(
        'phone', validators=[PhoneValidator()]
    )
    genres = SelectMultipleField(
        # COMPLETED: implement enum restriction
        'genres', validators=[DataRequired()],
        choices=[(choice.name, choice.value) for choice in Genre_Choices]
    )
    website = StringField(
      "website", validators=[Optional(), URL()]
    )
    facebook_link = StringField(
        'facebook_link', validators=[Optional(), URL()]
    )
    image_link = StringField(
      "image_link", validators=[Optional(), ImageLinkValidator()]
    )

class ArtistForm(FlaskForm):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=[
            ('AL', 'AL'),
            ('AK', 'AK'),
            ('AZ', 'AZ'),
            ('AR', 'AR'),
            ('CA', 'CA'),
            ('CO', 'CO'),
            ('CT', 'CT'),
            ('DE', 'DE'),
            ('DC', 'DC'),
            ('FL', 'FL'),
            ('GA', 'GA'),
            ('HI', 'HI'),
            ('ID', 'ID'),
            ('IL', 'IL'),
            ('IN', 'IN'),
            ('IA', 'IA'),
            ('KS', 'KS'),
            ('KY', 'KY'),
            ('LA', 'LA'),
            ('ME', 'ME'),
            ('MT', 'MT'),
            ('NE', 'NE'),
            ('NV', 'NV'),
            ('NH', 'NH'),
            ('NJ', 'NJ'),
            ('NM', 'NM'),
            ('NY', 'NY'),
            ('NC', 'NC'),
            ('ND', 'ND'),
            ('OH', 'OH'),
            ('OK', 'OK'),
            ('OR', 'OR'),
            ('MD', 'MD'),
            ('MA', 'MA'),
            ('MI', 'MI'),
            ('MN', 'MN'),
            ('MS', 'MS'),
            ('MO', 'MO'),
            ('PA', 'PA'),
            ('RI', 'RI'),
            ('SC', 'SC'),
            ('SD', 'SD'),
            ('TN', 'TN'),
            ('TX', 'TX'),
            ('UT', 'UT'),
            ('VT', 'VT'),
            ('VA', 'VA'),
            ('WA', 'WA'),
            ('WV', 'WV'),
            ('WI', 'WI'),
            ('WY', 'WY'),
        ]
    )
    phone = StringField(
        # COMPLETED implement validation logic for state (phone?)
        'phone', validators=[PhoneValidator()]
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        # COMPLETED implement enum restriction
        'genres', validators=[DataRequired()],
        choices=[(choice.name, choice.value) for choice in Genre_Choices]
    )
    website = StringField(
      "website", validators=[Optional(), URL()]
    )
    facebook_link = StringField(
        # TODO?? implement enum restriction?? (Probably a mistake) 
        "facebook_link", validators=[Optional(), URL()]
    )
    image_link = StringField(
      "image_link", validators=[Optional(), ImageLinkValidator()]
    )


# COMPLETED IMPLEMENT NEW ARTIST FORM AND NEW SHOW FORM
