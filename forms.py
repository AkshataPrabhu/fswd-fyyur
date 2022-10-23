from datetime import datetime
from flask_wtf import FlaskForm as Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, AnyOf, URL

import enums
import helperUtil
from enums import Genre


class ShowForm(Form):
    artist_id = StringField(
        'artist_id'
    )
    venue_id = StringField(
        'venue_id'
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default=datetime.today()
    )


class VenueForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=helperUtil.states_choices
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    phone = StringField(
        'phone'
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        # TODO implement enum restriction
        'genres', validators=[DataRequired()],
        choices=helperUtil.genre_choices
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL()]
    )
    website_link = StringField(
        'website_link'
    )

    seeking_talent = BooleanField('seeking_talent')

    seeking_description = StringField(
        'seeking_description'
    )

    def validate(self):
        print("valifinfg ")
        rv = Form.validate(self)
        if not rv:
            return False
        if not helperUtil.validate_phone(self.phone.data):
            self.phone.errors.append('Invalid phone number.')
            return False
        if not set(self.genres.data).issubset(dict(enums.Genre.choices()).keys()):
            self.genres.errors.append('Invalid genres.')
            return False
        if self.state.data not in dict(enums.State.choices()).keys():
            self.state.errors.append('Invalid state.')
            return False
        return True

class ArtistForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=helperUtil.states_choices
    )
    phone = StringField(
        # TODO implement validation logic for phone 
        'phone'
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],
        choices=helperUtil.genre_choices
    )
    facebook_link = StringField(
        # TODO implement enum restriction
        'facebook_link', validators=[URL()]
    )

    website_link = StringField(
        'website_link'
    )

    seeking_venue = BooleanField('seeking_venue')

    seeking_description = StringField(
        'seeking_description'
    )

    def validate(self):
        print("valifinfg ")
        rv = Form.validate(self)
        if not rv:
            return False
        if not helperUtil.validate_phone(self.phone.data):
            self.phone.errors.append('Invalid phone number.')
            return False
        # if not set(self.genres.data).issubset(dict(enums.Genre.choices()).keys()):
        #     self.genres.errors.append('Invalid genres.')
        #     return False
        # if self.state.data not in dict(enums.State.choices()).keys():
        #     self.state.errors.append('Invalid state.')
        #     return False
        return True