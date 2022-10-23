# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json

from flask_migrate import Migrate
import dateutil.parser
import babel
from flask import (Flask, render_template, request, Response,
                   flash, redirect, url_for)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from models import Venue, Artist, Shows, db
import config
from forms import *

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

# db = SQLAlchemy(app)
db.init_app(app)
# TODO: connect to a local postgresql database
migrate = Migrate(app, db)


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    data = []
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

    city_state_output = Venue.query.distinct(Venue.city, Venue.state).all()
    for cs in city_state_output:
        city_state_venue = {
            "city": cs.city,
            "state": cs.state
        }
        venue_by_city_state = Venue.query.filter_by(city=cs.city, state=cs.state).all()
        all_venues = []
        for venue in venue_by_city_state:
            all_venues.append({
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": len(list(filter(lambda x: x.start_time > datetime.now(), venue.shows)))
            })

        city_state_venue["venues"] = all_venues
        data.append(city_state_venue)

    return render_template('pages/venues.html', areas=data);


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get("search_term")

    response = {}
    count = 0
    data = []
    venues = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()

    for v in venues:
        venue = {
            "id": v.id,
            "name": v.name,
            "num_upcoming_shows": len(list(filter(lambda x: x.start_time > datetime.now(), v.shows)))
        }
        data.append(venue)
    response["count"] = len(venues)
    response["data"] = data

    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    venue = Venue.query.get(venue_id)
    print("Shows are ", venue.shows)
    upcoming_shows_obj = []
    past_shows_obj = []
    for u in venue.shows:
        temp = {
            "artist_id": u.artist_id,
            "artist_name": u.artist.name,
            "artist_image_link": u.artist.image_link,
            "start_time": str(u.start_time)
        }
        if datetime.now() < u.start_time:
            upcoming_shows_obj.append(temp)
        else:
            past_shows_obj.append(temp)
    # upcoming_shows = list(filter(lambda x: x.start_time > datetime.now(), venue.shows))
    # past_shows = list(filter(lambda x: x.start_time < datetime.now(), venue.shows))
    # for u in upcoming_shows:
    #     upcoming = {
    #         "artist_id": u.artist_id,
    #         "artist_name": u.artist.name,
    #         "artist_image_link": u.artist.image_link,
    #         "start_time": str(u.start_time)
    #     }
    #     upcoming_shows_obj.append(upcoming)
    # for p in past_shows:
    #     past = {
    #         "artist_id": p.artist_id,
    #         "artist_name": p.artist.name,
    #         "artist_image_link": p.artist.image_link,
    #         "start_time": str(p.start_time)
    #     }
    #     past_shows_obj.append(past)
    genres = venue.genres
    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website_link,
        "facebook_link": venue.website_link,
        "seeking_talent": venue.looking_for_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows_obj,
        "upcoming_shows": upcoming_shows_obj,
        "past_shows_count": len(past_shows_obj),
        "upcoming_shows_count": len(upcoming_shows_obj),
    }
    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    form = VenueForm(request.form, meta={'csrf': False})
    if form.validate():
        try:
            venue = Venue(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                address=form.address.data,
                phone=form.phone.data,
                genres=form.genres.data,
                website_link=form.website_link.data,
                image_link=form.image_link.data,
                facebook_link=form.facebook_link.data,
                looking_for_talent=form.seeking_talent.data,
                seeking_description=form.seeking_description.data,
            )

            db.session.add(venue)
            db.session.commit()
            # on successful db insert, flash success
            flash('Venue ' + request.form['name'] + ' was successfully listed!')
        except:
            db.session.rollback()
            # TODO: on unsuccessful db insert, flash an error instead.
            flash('An error occurred. Venue ' + request.form['name'] + ' could not be created.')
        finally:
            db.session.close()
    else:
        message = []
        for field, err in form.errors.items():
            message.append(field + ' ' + '|'.join(err))
        flash('Errors/invalid values in ' + str(message))
        form = VenueForm()
        return render_template('forms/new_venue.html', form=form)
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        v = Venue.query.get(venue_id)
        db.session.delete(v)
        db.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    artists = Artist.query.distinct().all()
    data = []
    for a in artists:
        artist = {
            "id": a.id,
            "name": a.name
        }
        data.append(artist)

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get("search_term")

    response = {}
    count = 0
    data = []
    artists = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()

    for a in artists:
        artist = {
            "id": a.id,
            "name": a.name,
            "num_upcoming_shows": len(list(filter(lambda x: x.start_time > datetime.now(), a.shows)))
        }
        data.append(artist)
    response["count"] = len(artists)
    response["data"] = data
    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    artist = Artist.query.get(artist_id)

    upcoming_shows_obj = []
    past_shows_obj = []
    for u in artist.shows:
        temp = {
            "venue_id": u.venue_id,
            "venue_name": u.venue.name,
            "venue_image_link": u.venue.image_link,
            "start_time": str(u.start_time)
        }
        if datetime.now() < u.start_time:
            upcoming_shows_obj.append(temp)
        else:
            past_shows_obj.append(temp)
    # upcoming_shows = list(filter(lambda x: x.start_time > datetime.now(), artist.shows))
    # past_shows = list(filter(lambda x: x.start_time < datetime.now(), artist.shows))
    # upcoming_shows_obj = []
    # past_shows_obj = []
    # for u in upcoming_shows:
    #     upcoming = {
    #         "venue_id": u.venue_id,
    #         "venue_name": u.venue.name,
    #         "venue_image_link": u.venue.image_link,
    #         "start_time": str(u.start_time)
    #     }
    #     upcoming_shows_obj.append(upcoming)
    # for p in past_shows:
    #     past = {
    #         "venue_id": p.venue_id,
    #         "venue_name": p.venue.name,
    #         "venue_image_link": p.venue.image_link,
    #         "start_time": str(p.start_time)
    #     }
    #     past_shows_obj.append(past)
    genres = artist.genres
    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website_link,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.looking_for_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows_obj,
        "upcoming_shows": upcoming_shows_obj,
        "past_shows_count": len(past_shows_obj),
        "upcoming_shows_count": len(upcoming_shows_obj),
    }

    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.image_link.data = artist.image_link
    form.facebook_link.data = artist.facebook_link
    form.genres.data = artist.genres
    form.website_link.data = artist.website_link
    form.seeking_venue.data = artist.looking_for_venue
    form.seeking_description.data = artist.seeking_description

    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    artist = Artist.query.get(artist_id)
    aform = ArtistForm(request.form, meta={"csrf": False})

    if aform.validate():
        try:

            artist.name=aform.name.data
            artist.city=aform.city.data
            artist.state=aform.state.data
            artist.phone=aform.phone.data
            artist.image_link=aform.image_link.data
            artist.facebook_link=aform.facebook_link.data
            artist.genres=aform.genres.data
            artist.website_link=aform.website_link.data
            artist.looking_for_venue=aform.seeking_venue.data
            artist.seeking_description=aform.seeking_description.data
            db.session.add(artist)
            db.session.commit()
            # on successful db insert, flash success
            flash('Artist ' + request.form['name'] + ' was successfully listed!')
        except:
            db.session.rollback()
            flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
        finally:
            db.session.close()
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')

    else:
        message = []
        for field, err in aform.errors.items():
            message.append(field + ' ' + '|'.join(err))
        flash('Errors/invalid values in ' + str(message))
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.get(venue_id)
    genre = venue.genres
    form = VenueForm()
    form.name.data = venue.name
    form.genres.data = genre
    form.address.data = venue.address
    form.city.data = venue.city
    form.state.data = venue.state
    form.phone.data = venue.phone
    form.website_link.data = venue.website_link
    form.facebook_link.data = venue.facebook_link
    form.seeking_talent.data = venue.looking_for_talent
    form.seeking_description.data = venue.seeking_description
    form.image_link.data = venue.image_link
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    venue = Venue.query.get(venue_id)
    form = VenueForm(request.form, meta={'csrf': False})

    if form.validate():
        try:
            venue.name = form.name.data
            venue.city = form.city.data
            venue.state = form.state.data
            venue.address = form.address.data
            venue.phone = form.phone.data
            venue.genres = form.genres.data
            venue.website_link = form.website_link.data
            venue.image_link = form.image_link.data
            venue.facebook_link = form.facebook_link.data
            venue.looking_for_talent = form.seeking_talent.data
            venue.seeking_description = form.seeking_description.data

            db.session.add(venue)
            db.session.commit()
            # on successful db insert, flash success
            flash('Venue ' + request.form['name'] + ' was successfully listed!')
        except:
            db.session.rollback()
            # TODO: on unsuccessful db insert, flash an error instead.
            flash('An error occurred. Venue ' + request.form['name'] + ' could not be created.')
        finally:
            db.session.close()
    else:
        message = []
        for field, err in form.errors.items():
            message.append(field + ' ' + '|'.join(err))
        flash('Errors/invalid values in ' + str(message))
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
    form = ArtistForm(request.form, meta={"csrf": False})

    if form.validate():
        try:
            artist = Artist(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                phone=form.phone.data,
                image_link=form.image_link.data,
                facebook_link=form.facebook_link.data,
                genres=form.genres.data,
                website_link=form.website_link.data,
                looking_for_venue=form.seeking_venue.data,
                seeking_description=form.seeking_description.data
            )
            db.session.add(artist)
            db.session.commit()
            # on successful db insert, flash success
            flash('Artist ' + request.form['name'] + ' was successfully listed!')
        except:
            db.session.rollback()
            flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
        finally:
            db.session.close()
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')

    else:
        message = []
        for field, err in form.errors.items():
            message.append(field + ' ' + '|'.join(err))
        flash('Errors/invalid values in ' + str(message))
        form = ArtistForm()
        return render_template('forms/new_artist.html', form=form)
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    shows = Shows.query.all()
    data = []
    for s in shows:
        show_data = {
            "venue_id": s.venue.id,
            "venue_name": s.venue.name,
            "artist_id": s.artist.id,
            "artist_name": s.artist.name,
            "artist_image_link": s.artist.image_link,
            "start_time": str(s.start_time)
        }
        data.append(show_data)

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
    form = ShowForm(request.form, meta={"csrf": False})
    if form.validate():
        try:
            show = Shows(
                venue_id=form.venue_id.data,
                artist_id=form.artist_id.data,
                start_time=form.start_time.data
            )
            db.session.add(show)
            db.session.commit()
            # on successful db insert, flash success
            flash('Show was successfully added!')
        except:
            db.session.rollback()
            # TODO: on unsuccessful db insert, flash an error instead.
            # e.g., flash('An error occurred. Show could not be listed.')
            flash('An error occurred. Show could not be added.')
        finally:
            db.session.close()
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

    else:
        message = []
        for field, err in form.errors.items():
            message.append(field + ' ' + '|'.join(err))
        flash('Errors/invalid values in ' + str(message))
        form = ShowForm()
        return render_template('forms/new_show.html', form=form)
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

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
