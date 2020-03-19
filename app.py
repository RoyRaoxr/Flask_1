# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy.orm import Session
from sqlalchemy.sql import expression
from sqlalchemy import func, desc

from forms import *
from flask_migrate import Migrate

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)


# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String))
    seeking_talent = db.Column(db.BOOLEAN, server_default=expression.false())
    seeking_description = db.Column(db.String(120), default="")
    website = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(500))
    artists = db.relationship('Artist', secondary='show')

    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'
    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(500))
    website = db.Column(db.String(500))
    seeking_venue = db.Column(db.BOOLEAN, server_default=expression.false())
    seeking_description = db.Column(db.String(500))
    venues = db.relationship('Venue', secondary='show')

    def __repr__(self):
        return f'<Artist {self.id} {self.name}>'
    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Show(db.Model):
    __tablename__ = 'show'

    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<Show {self.artist_id} {self.venue_id} {self.start_time}>'


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

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
    locations = Venue.query.with_entities(Venue.city, Venue.state).distinct()
    data = list()
    for location in locations:
        single_location = {}
        venue_list = []
        single_location['city'] = location[0]
        single_location['state'] = location[1]
        query_venues = Venue.query \
            .filter_by(city=location[0], state=location[1]) \
            .with_entities(Venue.id, Venue.name) \
            .order_by('id') \
            .all()
        for v in query_venues:
            venue_data = {
                'id': v[0],
                'name': v[1],
                'num_upcoming_shows': Show.query.filter_by(venue_id=v[0]).filter(
                    Show.start_time >= datetime.now())
            }
            venue_list.append(venue_data)
        single_location['venues'] = venue_list
        data.append(single_location)
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    #   seach for Hop should return "The Musical Hop".
    #   search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_name = request.form.get('search_term', '')
    results = Venue.query.filter(Venue.name.contains(search_name)).all()
    response = {
        "count": len(results),
    }
    data = []
    for r in results:
        data.append({
            'id': r.id,
            'name': r.name,
            'num_upcoming_shows': Show.query.filter_by(venue_id=r.id).filter(
                Show.start_time >= datetime.now()).count()
        })
    response['data'] = data
    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    venue = Venue.query.get(venue_id)
    if venue is None:
        return render_template('errors/404.html')
    shows = Show.query.filter_by(venue_id=venue_id)
    data = {
        'id': venue_id,
        'name': venue.name,
        'genres': venue.genres,
        'address': venue.address,
        'city': venue.city,
        'state': venue.state,
        'phone': venue.phone,
        'website': venue.website,
        'facebook_link': venue.facebook_link,
        'seeking_description': venue.seeking_description,
        'seeking_talent': venue.seeking_talent,
        'image_link': venue.image_link
    }
    past_show = []
    upcoming_show = []
    for show in shows.filter(Show.start_time < datetime.now()).all():
        past = {
            'artist_id': show.artist_id,
            'artist_name': Artist.query.get(show.artist_id).name,
            'artist_image_link': Artist.query.get(show.artist_id).image_link,
            'start_time': str(show.start_time)
        }
        past_show.append(past)
    for show in shows.filter(Show.start_time >= datetime.now()).all():
        coming = {
            'artist_id': show.artist_id,
            'artist_name': Artist.query.get(show.artist_id).name,
            'artist_image_link': Artist.query.get(show.artist_id).image_link,
            'start_time': str(show.start_time)
        }
        upcoming_show.append(coming)
    data['past_shows'] = past_show
    data['upcoming_shows'] = upcoming_show
    data['past_shows_count'] = len(past_show)
    data['upcoming_shows_count'] = len(upcoming_show)

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
    error = False
    form = VenueForm(request.form)
    try:
        print(request.form)
        if form.validate():
            name = form.name.data
            city = form.city.data
            state = form.state.data
            address = form.address.data
            phone = form.phone.data
            genres = form.genres.data
            image_link = form.image_link.data
            seeking_description = form.seeking_description.data
            seeking_talent = True if seeking_description is not "" else False
            facebook_link = form.facebook_link.data
            venue = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres,
                          image_link=image_link, seeking_talent=seeking_talent, seeking_description=seeking_description,
                          facebook_link=facebook_link)
            db.session.add(venue)
            db.session.commit()
        else:
            flash("Form Validation Failed, Check Form Data Format")
            return render_template('forms/new_venue.html', form=form)
    except:
        error = True
        db.session.rollback()
        flash('Error occurred ! Venue  ' + request.form['name'] + ' was not inserted')
        return redirect('')
    finally:
        db.session.close()
    if not error:
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    else:
        return render_template('errors/500.html')
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    error = False
    try:
        show = Show.query.filter_by(venue_id=venue_id).delete()
        venue = Venue.query.filter_by(id=venue_id).delete()
        db.session.execute("SELECT setval ('venue_id_seq', max(venue.id)) FROM venue;")
        if len(Venue.query.all()) is 0:
            db.session.execute("ALTER SEQUENCE venue_id_seq RESTART WITH 1;")
            db.session.commit()
        else:
            db.session.commit()
        flash('Success to Delete Venue' + venue_id + 'and Show' + show.id + '! Good!')
    except:
        error = True
        db.session.rollback()
        flash('Fail to Delete Venue' + venue_id + '! Something Wrong!')
    finally:
        db.session.close()
    if not error:
        flash('Success to Delete Venue' + venue_id + '! Good!')
    else:
        return render_template('errors/500.html')
    # TODO: Complete this endpoint for taking a venue_id, and using
    #       SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    #       BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    #       clicking that button delete it from the db then redirect the user to the homepage
    return render_template('pages/home.html')


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    data = []
    artists_objects = Artist.query.all()
    for artist in artists_objects:
        dic = {
            'id': artist.id,
            'name': artist.name
        }
        data.append(dic)
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    #   search for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    #   search for "band" should return "The Wild Sax Band".
    search_name = request.form.get('search_term', '')
    results = Artist.query.filter(Artist.name.contains(search_name)).all()
    response = {
        "count": len(results),
    }
    data = []
    for r in results:
        data.append({
            'id': r.id,
            'name': r.name,
            'num_upcoming_shows': Show.query.filter_by(artist_id=r.id).filter(
                Show.start_time >= datetime.now()).count()
        })
    response['data'] = data
    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    artist = Artist.query.get(artist_id)
    shows = Show.query.filter_by(artist_id=artist_id)
    data = {
        'id': artist_id,
        'name': artist.name,
        'genres': artist.genres,
        'city': artist.city,
        'state': artist.state,
        'phone': artist.phone,
        'website': artist.website,
        'facebook_link': artist.facebook_link,
        'seeking_description': artist.seeking_description,
        'image_link': artist.image_link
    }
    past_show = []
    upcoming_show = []
    for show in shows.filter(Show.start_time < datetime.now()).all():
        past = {
            'venue_id': show.venue_id,
            'venue_name': Venue.query.get(show.venue_id).name,
            'venue_image_link': Venue.query.get(show.venue_id).image_link,
            'start_time': str(show.start_time)
        }
        past_show.append(past)
    for show in shows.filter(Show.start_time >= datetime.now()).all():
        coming = {
            'venue_id': show.venue_id,
            'venue_name': Venue.query.get(show.venue_id).name,
            'venue_image_link': Venue.query.get(show.venue_id).image_link,
            'start_time': str(show.start_time)
        }
        upcoming_show.append(coming)
    data['past_shows'] = past_show
    data['upcoming_shows'] = upcoming_show
    data['past_shows_count'] = len(past_show)
    data['upcoming_shows_count'] = len(upcoming_show)

    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    form.name.data = artist.name
    form.genres.data = artist.genres
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.website.data = artist.website
    form.facebook_link.data = artist.facebook_link
    form.seeking_description.data = artist.seeking_description
    form.image_link.data = artist.image_link
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    #   artist record with ID <artist_id> using the new attributes
    artist = Artist.query.get(artist_id)
    form = ArtistForm(request.form)
    try:
        if form.validate():
            artist.name = form.name.data
            artist.genres = form.genres.data
            artist.city = form.city.data
            artist.state = form.state.data
            artist.phone = form.phone.data
            artist.facebook_link = form.facebook_link.data
            db.session.commit()
        else:
            flash("Edit Form Validation Failed, Please Resubmit")
            return redirect(url_for('show_artist', artist_id=artist_id))
    except:
        db.session.rollback()
        flash("Something Wrong During Submit!")
        return redirect(url_for('show_artist', artist_id=artist_id))
    finally:
        db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    form.name.data = venue.name
    form.genres.data = venue.genres
    form.address.data = venue.address
    form.city.data = venue.city
    form.state.data = venue.state
    form.phone.data = venue.phone
    form.website.data = venue.website
    form.facebook_link.data = venue.facebook_link
    form.seeking_description.data = venue.seeking_description
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    #   venue record with ID <venue_id> using the new attributes
    try:
        form = VenueForm(request.form)
        if form.validate():
            venue = Venue.query.get(venue_id)
            venue.name = form.name.data
            venue.genres = form.genres.data
            venue.address = form.address.data
            venue.city = form.city.data
            venue.state = form.state.data
            venue.phone = form.phone.data
            venue.website = form.website.data
            venue.facebook_link = form.facebook_link.data
            venue.seeking_description = form.seeking_description.data
            venue.seeking_talent = True if venue.seeking_description is not "" else False
            venue.image_link = form.image_link.data
            db.session.commit()
        else:
            flash("Form Validation Failed")
    except:
        db.session.rollback()
        flash("Wrong Update")
        return redirect(url_for('show_venue', venue_id=venue_id))
    finally:
        db.session.close()
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
    error = False
    form = ArtistForm(request.form)
    try:
        name = form.name.data
        city = form.city.data
        state = form.state.data
        phone = form.phone.data
        seeking_description = form.seeking_description.data
        image_link = form.image_link.data
        genres = form.genres.data
        facebook_link = form.facebook_link.data
        seeking_venue = True if seeking_description is not "" else False
        artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres,
                        image_link=image_link, seeking_venue=seeking_venue, seeking_description=seeking_description,
                        facebook_link=facebook_link)
        db.session.add(artist)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        flash('Error occurred ! Artist  ' + form.name.data + ' was not inserted')
    finally:
        db.session.close()
    if not error:
        flash('Artist ' + form.name.data + ' was successfully listed!')
    else:
        return render_template('errors/500.html')
    # on successful db insert, flash success
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
    results = db.session.query(Show, Venue, Artist).join(Venue).join(Artist).all()
    data = []
    for result in results:
        data.append({
            'venue_id': result[1].id,
            'venue_name': result[1].name,
            'artist_id': result[2].id,
            'artist_name': result[2].name,
            'artist_image_link': result[2].image_link,
            'start_time': str(result[0].start_time)
        })
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
    error = False
    form = ShowForm(request.form)
    try:
        artist_id = form.artist_id.data
        venue_id = form.venue_id.data
        start_time = form.start_time.data
        show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
        db.session.add(show)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if not error:
        flash('Show was successfully listed!')
    else:
        flash('Error occurred ! Show ' + ' was not inserted')
        return render_template('errors/500.html')

    # on successful db insert, flash success
    # TODO: on unsuccessful db insert, flash an error instead.
    #   e.g., flash('An error occurred. Show could not be listed.')
    #   see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
