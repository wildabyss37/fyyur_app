#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres: @localhost:5432/fyyurapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Artist (db.Model):
    __tablename__ = 'artist'
    id = db.Column (db.Integer, primary_key=True)
    name = db.Column (db.String(150), nullable=False)
    city = db.Column (db.String(150), nullable=False)
    state = db.Column (db.String(150), nullable=False)
    phone = db.Column (db.String(150), nullable=False)
    address = db.Column (db.String(120), nullable=False)
    genres = db.Column (db.String(200), nullable=False)
    facebook_link = db.Column (db.String(120))
    image_link = db.Column (db.String(500))
    website = db.Column (db.String(150), nullable=False)
    
    def __repr__(self):
      return f'<Artist: {self.id}, name: {self.name}, city: {self.city}, state: {self.state}, phone: {self.phone}, address: {self.address}, genres: {self.genres}, facebook_link: {self.facebook_link}, image_link: {self.image_link} >'


class Venue (db.Model):
    __tablename__ = 'venue' 
    id = db.Column (db.Integer, primary_key=True)
    name = db.Column (db.String(150), nullable=False)
    city = db.Column (db.String(120), nullable=False)
    state = db.Column (db.String(150), nullable=False)
    address = db.Column(db.String(120),nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(300), nullable=False)
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(120), nullable=False)
    # shows = db.Relationship('Show', backref='venue', lazy=False)
    
    def __repr__(self):
      return f'<Venue: {self.id}, name: {self.name}, city: {self.city}, state: {self.state}, address: {self.address}, phone: {self.phone}, facebook_link: {self.facebook_link}, image_link: {self.image_link}, genres: {self.genres}, website: {self.website}, shows: {self.shows}>'


class Show(db.Model):
    __tablename__ = 'show'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey("artist.id"), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey("venue.id"), nullable=False)

    def __repr__(self):
      return f'<Show {self.id}, date: {self.date}, artist_id: {self.artist_id}, venue_id: {self.venue_id}>'


# TODO: implement any missing fields, as a database migration using Flask-Migrate
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


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
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  # num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    areas = []
    data = Venue.query.order_by('city', 'state', 'name').all()
    for place in data:
      area_item = {}
      loc_area = -1
      if len(areas) == 0:
        loc_area = 0
        area_item = {
        "city" : place.city,
        "state": place.state,
        "venues": []
      }
      areas.append(area_item)
    else:
      for i, area in enumerate(areas):
        if area['city'] == place.city and area['state'] == place.state:
          loc_area = i
          break
      if loc_area < 0:
        area_item = {
          "city": place.city,
          "state": place.state,
          "venues": []
        }
        areas.append(area_item)
        loc_area = len(areas) - 1
      else:
        area_item = areas[loc_area]
        v = {
        "id": place.id,
        "name": place.name,
        "num_upcoming_shows": 5
        # num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
        }
    area_item['venues'].append(v)
    areas[loc_area] = area_item

    return render_template('pages/venues.html', areas=areas)
  

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_name = request.form.get('search_name')
    search = "%{}%".format(search_name.replace(" ", "\ "))
    data = Artist.query.filter(Artist.name.match(search)).order_by('name').all()
    items = []
    for row in data:
      aux = {
      "id": row.id,
      "name": row.name,
      # "" :
    }
    items.append(aux)

    response={
    "count": len(items),
    "data": items
  }

    return render_template('pages/search_venues.html', results=response, search_name=request.form.get('search_name', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data = Venue.query.filter_by(id=venue_id).first()
  data.genres = json.loads(data.genres)
  upcoming_shows = []
  past_shows = []
  for show in data.shows:
    if show.date > datetime.now():
      upcoming_shows.append(show)
    else:
      past_shows.append(show)
  data.upcoming_shows = upcoming_shows
  data.past_shows = past_shows

  return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    app = Flask(__name__)
    csrf.init_app(app)
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
    app = Flask(__name__)
    csrf.init_app(app)
    error = False
    body = {}
    request_data = request.get_json()
    try:
      name = request_data['name']
      city = request_data['city']
      state = request_data['state']
      phone = request_data['phone']
      address = request_data['address']
      genres = json.dumps(request_data['genres'])
      facebook_link = request_data['facebook_link']
      image_link = request_data['image_link']
      website = request_data['website']
      venue = Venue(name=name, city=city, state=state, phone=phone, address=address, genres=genres, facebook_link=facebook_link, image_link=image_link, website=website)
      db.session.add(venue)
      db.session.commit()
    except:
      db.session.rollback()
      error = True
      print(sys.exc_info())
    finally:
      db.session.close()
    if error:
      abort(500)
      body['success'] = False
      flash('An error occurred. Venue'  + data.name + ' could not be listed.')
      body['msg'] = ' An error occured '
    else:
      # on successful db insert, flash success
      body['success'] = True
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  
      return jsonify(body)



  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  data = Venue.query.filter_by(venue_id).delete()

  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = Artist.query.order_by('name').all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  
    search_term = request.form.get('search_term')
    search = "%{}%".format(search_term.replace(" ", "\ "))
    data = Artist.query.filter(Artist.name.match(search)).order_by('name').all()
    items = []
    for row in data:
      aux = {
      "id": row.id,
      "name": row.name,
      "num_upcoming_shows": len(row.shows)
    }
    items.append(aux)
    response={
        "count": len(items),
        "data": items
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
    data = Artist.query.filter_by(id=artist_id).first()
    data.genres = json.loads(data.genres)

    upcoming_shows = []
    past_shows = []
    for show in data.shows:
      if show.date > datetime.now():
        upcoming_shows.append(show)
      else:
        past_shows.append(show)
    data.upcoming_shows = upcoming_shows
    data.past_shows = past_shows

    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist= Artist.query.filter_by(id=artist_id).first()

    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.facebook_link.data = artist.facebook_link
    form.website.data = artist.website
    form.image_link.data = artist.image_link
    form.genres.data = json.loads(artist.genres)
    # TODO: populate form with fields from artist with ID <artist_id>  
    
    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
    app = Flask(__name__)
    csrf.init_app(app)
    error = False
    body = {}
    request_data = request.get_json()
    try:
      artist = Artist.query.filter_by(id=artist_id).first()
      artist.name = request_data['name']
      artist.city = request_data['city']
      artist.state = request_data['state']
      artist.phone = request_data['phone']
      artist.genres = json.dumps(request_data['genres'])
      artist.facebook_link = request_data['facebook_link']
      artist.website = request_data['website']
      artist.image_link = request_data['image_link']
      db.session.add(artist)
      db.session.commit()
    except:
      db.session.rollback()
      error = True
      print(sys.exc_info())
    finally:
      db.session.close()
    if error:
      abort(500)
      body['success'] = False
      body['msg'] = 'There was an error '
    else:
      body['msg'] = 'That create was sucessfully'
      body['success'] = True

    return jsonify(body)
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    place = Venue.query.filter_by(id=venue_id).first()

    form.name.data = place.name
    form.city.data = place.city
    form.state.data = place.state
    form.phone.data = place.phone
    form.address.data = place.address
    form.facebook_link.data = place.facebook_link
    form.website.data = place.website
    form.image_link.data = place.image_link
    form.genres.data = json.loads(place.genres)
  
    return render_template('forms/edit_venue.html', form=form, place=place)

  # TODO: populate form with values from venue with ID <venue_id>

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
    app = Flask(__name__)
    csrf.init_app(app)
    error = False
    body = {}
    request_data = request.get_json()
    try:
      place = Venue.query.filter_by(id=venue_id).first()
      place.name = request_data['name']
      place.city = request_data['city']
      place.state = request_data['state']
      place.phone = request_data['phone']
      place.address = request_data['address']
      place.genres = json.dumps(request_data['genres'])
      place.facebook_link = request_data['facebook_link']
      place.website = request_data['website']
      place.image_link = request_data['image_link']
      db.session.add(place)
      db.session.commit()
    except:
      db.session.rollback()
      error = True
      print(sys.exc_info())
    finally:
      db.session.close()
    if error:
      abort(500)
      body['success'] = False
      body['msg'] = 'There was an error '
    else:
      body['msg'] = 'That create was sucessfully'
      body['success'] = True
    
    return jsonify(body)
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    app = Flask(__name__)
    csrf.init_app(app)
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
    app = Flask(__name__)
    csrf.init_app(app)
    error = False
    body = {}
    request_data = request.get_json()


  # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  rows = db.session.query(Show, Artist, Venue).join(Artist).join(Venue).filter(Show.date > datetime.now()).order_by('date').all()
  data = []
  for row in rows:
    item = {
      'venue_id': row.Venue.id,
      'artist_id': row.Artist.id,
      'venue_name': row.Venue.name,
      'artist_name': row.Artist.name,
      'artist_image_link': row.Artist.image_link,
      'start_time': row.Show.date.strftime('%Y-%m-%d %H:%I')
    }
    data.append(item)
  
    return render_template('pages/shows.html', shows=data)
  


@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  app = Flask(__name__)
  csrf.init_app(app)
  error = False
  body = {}
  request_data = request.get_json()
  try:
    artist_id = request_data['artist_id']
    venue_id = request_data['venue_id']
    start_time = request_data['start_time']

    show = Show(artist_id=artist_id, venue_id=venue_id, date=start_time)
    db.session.add(show)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    abort(500)
    body['success'] = False
    body['msg'] = 'There an error '
  else:
    # on successful db insert, flash success
    body['success'] = True
    flash('Show was successfully listed!')
    body['msg'] = 'That create was sucessfully'

    return jsonify(body)


  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
#   return render_template('pages/home.html')

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
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
